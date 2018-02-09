import requests
import json
import time
import logging
import ipaddress
import pandas as pd
# from vcr import use_cassette
from copy import deepcopy
from ripe.atlas.cousteau import ProbeRequest
from pymongo.errors import DuplicateKeyError, BulkWriteError
from pymongo import MongoClient, ASCENDING
from constants import cc_to_rir
from my_key import ATLAS_API_KEY

ITER_T = 30  # Number of targets per request
ITER_P = 50  # Number of probes per request


URL = ('https://atlas.ripe.net/api/v2/measurements/?key={}'
       .format(ATLAS_API_KEY)
       )
URL_O = ('https://atlas.ripe.net/api/v2/measurements/my/?key={}&status=2'
         .format(ATLAS_API_KEY)
         )

LOG_FILE_NAME = 'log.log'


def get_db(db_name):
    client = MongoClient(host='mongodb')
    db = client.get_database(db_name)
    db.probes.create_index('id', unique=True)
    db.measurements.create_index('id', unique=True)
    db.results.create_index([('from', ASCENDING),
                             ('dst_addr', ASCENDING),
                             ('msm id', ASCENDING)], unique=True)
    db.campaign_descriptor.create_index(
            [('i_target', ASCENDING),
             ('i_probe', ASCENDING)], unique=True)
    logging.basicConfig(filename=db_name + '.log', level=logging.DEBUG)
    return db


def get_probes(clean=True):
    all_probes = []
    filters = {"tags": ["system-ipv6-works", "system-v3"]}
    probes = ProbeRequest(**filters)
    for p in probes:
        all_probes.append(p)
    df = pd.DataFrame(all_probes)
    if not clean:
        return df
    df = df[(df.address_v6 is not None) & (df.is_public)]
    df.country_code = df.country_code.str.decode('unicode-escape')
    df['rir'] = df.country_code.map(cc_to_rir)
    df.set_index('id', inplace=True)
    df.drop(
        ['address_v4',
         'asn_v4',
         'description',
         'first_connected',
         'geometry',
         'is_anchor',
         'is_public',
         'last_connected',
         'prefix_v4',
         'status',
         'status_since',
         'tags',
         'total_uptime',
         'type'
         ], axis=1, inplace=True)
    df.columns = ['address', 'asn', 'cc', 'prefix', 'rir']
    return df


# def get_probes(directory, clean):
#     return use_cassette(directory)(_get_probes)(clean)


def get_probes_by_country_v6(COUNTRY_LIST, db):
    """
    Finds all probes in the specified countries running
    ripe atlas v3 and with working ipv6
    """
    for cc in COUNTRY_LIST:
        filters = {
                    "tags": ["system-ipv6-works", "system-v3"],
                    "country_code": cc,
                   }
        probes = ProbeRequest(**filters)
        for p in probes:
            try:
                db.probes.insert_one(p)
            except DuplicateKeyError as e:
                logging.info(e)


# def get_probes_by_country_v6(directory, COUNTRY_LIST, db):
#     return use_cassette(directory)(
#         _get_probes_by_country_v6)(COUNTRY_LIST=COUNTRY_LIST, db=db)


def new_campaign(duration=60*60*22):
    return {
        "definitions": [],
        "probes": [],
        "is_oneoff": False,
        "stop_time": duration
    }


def probes_to_dict(probe_list):
    """
    Add the id of each probe in probe_list to the probe
    section of the campaign.
    Everything should return a copy.
    """
    probe_dict = {
       "value": '',
       "type": "probes",
       "requested": 1
      }
    probe_dict_list = []
    for probe in probe_list:
        new_probe_dict = deepcopy(probe_dict)
        new_probe_dict['value'] = probe
        probe_dict_list.append(new_probe_dict)
    return probe_dict_list


def targets_to_dict(target_list):
    """
    Adds a new description in the campaign for each IP
    address in target_list. IP addresses can be either v4 or
    v6. Addresses are excepted to be unicode strings
    """
    definition_dict = {
       "target": '',
       "af": 1,
       "timeout": 4000,
       "description": "",
       "protocol": "ICMP",
       "interval": 86400,
       "resolve_on_probe": False,
       "packets": 10,
       "size": 48,
       "first_hop": 1,
       "max_hops": 32,
       "paris": 16,
       "destination_option_size": 0,
       "hop_by_hop_option_size": 0,
       "dont_fragment": False,
       "skip_dns_check": True,
       "type": "traceroute"
      }

    target_dict_list = []
    for addr in target_list:
        version = ipaddress.ip_address(addr).version
        new_probe_dict = deepcopy(definition_dict)
        new_probe_dict['target'] = addr
        new_probe_dict['af'] = version
        new_probe_dict['description'] = 'trace to ' + addr
        target_dict_list.append(new_probe_dict)
    return target_dict_list


def save_campaign(target_list,
                  probe_list,
                  db,
                  description='',
                  tag=''):
    """
    Given the targets IP of the campaign and the list of probes to
    be used saves in the collection :campaign_descriptor: several
    json documetns. Each of them contains the information to a carry
    a measurement from serveral probes (not all of them) to 1 IP.
    The maximum number of probes to be includes in each measurement
    is ITER_P. Description and tag atributes are for user reference.
    The primary-key of a descriptor is (i_target, i_probe), used to
    iterate over the targets and groups of probes.
    Each descriptor has an attribute :status: with 3 posible states:
    waiting (the measurement hasn't been created in RIPE),
    ongoing (the measurement is still running in RIPE),
    finished( the measurement has stopped running and the results are
    PROBABLY stored in the database)
    """
    cant_targets, cant_probes = len(target_list), len(probe_list)
    failed_inserts = []
    for i_target in range(cant_targets):
        for i_probe in range(0, cant_probes, ITER_P):
            campaign_batch = new_campaign()
            campaign_batch['definitions'] = [target_list[i_target]]
            campaign_batch['probes'] = (
                probe_list[i_probe:i_probe+ITER_P])
            campaign_batch['tag'] = tag
            campaign_batch['description'] = description
            campaign_batch['i_target'] = i_target
            campaign_batch['i_probe'] = int(i_probe//ITER_P)
            campaign_batch['status'] = 'waiting'
            try:
                db.campaign_descriptor.insert(deepcopy(campaign_batch))
            except:
                failed_inserts.append(campaign_batch)

    logging.info(failed_inserts)
    return True


def schedule_batch(n, db):
    failed_inserts = []
    if n:
        schedule_list = list((db
                              .campaign_descriptor
                              .find({'status': 'waiting'}).limit(n)
                              ))
        for batch in schedule_list:
            new_dict = dict((key, value) for key, value in batch.iteritems() if
                            key in ['probes',
                                    'definitions',
                                    'is_oneoff',
                                    'stop_time']
                            )
            new_dict['stop_time'] = new_dict['stop_time'] + int(time.time())
            resp = requests.post(URL, json=new_dict)
            if resp.status_code == 201:
                msm_id = json.loads(resp.content)['measurements'][0]
                try:
                    (db
                     .campaign_descriptor
                     .update_one({'_id': batch['_id']},
                                 {'$set':
                                 {'status': 'ongoing',
                                  'msm_id': msm_id,
                                  'stop_time': new_dict['stop_time']}},
                                 upsert=False)
                     )
                except:
                    failed_inserts.append(msm_id)
            else:
                print 'Measurement creation failed, again in scheduling queue'
    return failed_inserts


def count_ongoing():
    res = requests.get(URL_O)
    if res.status_code == 200:
        res = json.loads(res.content)
        return int(res['count'])
    else:
        return False


def report_status(db):
    cnt_waiting = db.campaign_descriptor.find({'status': 'waiting'})
    cnt_ongoing = db.campaign_descriptor.find({'status': 'ongoing'})
    cnt_finished = db.campaign_descriptor.find({'status': 'finished'})
    print 'Status'
    print 'DB, Waiting for creation: {}'.format(cnt_waiting.count())
    print 'DB, Ongoing on platform: {}'.format(cnt_ongoing.count())
    print 'DB, Finished: {}'.format(cnt_finished.count())


def scheduler(db, sleep_time=1, wait_time=60):
    cant_ongoing = count_ongoing()
    schedule_batch(n=(100 - cant_ongoing), db=db,)
    print 'going to sleep...zzz...'
    time.sleep(wait_time)
    print 'waking up...'
    recover_results(db, sleep_time)
    report_status(db)


def recover_results(db, sleep_time, final_check=False):

    pending_list = list(db
                        .campaign_descriptor
                        .find({'$and': [{'msm_id': {'$exists': True}},
                                        {'status': 'ongoing'}]})
                        )
    if final_check:
        pending_list = list(db
                            .campaign_descriptor
                            .find({'$and': [{'msm_id': {'$exists': True}},
                                            {'status': 'finished'}]})
                            )
    print len(pending_list)
    for batch in pending_list:
        chk_id = batch['msm_id']
        URL_M = (
                'https://atlas.ripe.net:443/api/v2/measurements/{}/?key={}'
                .format(str(chk_id), ATLAS_API_KEY)
                )
        time.sleep(sleep_time)
        measurement = requests.get(URL_M)
        if measurement.status_code == 200:
            measurement_json = json.loads(measurement.content)

            results = requests.get(measurement_json['result'])
            excpected_results = measurement_json['probes_scheduled']
            timedout = (batch['stop_time'] - time.time()) < 75600
            if results.status_code == 200:
                results_json = json.loads(results.content)
                aux_var = []
                for mini_json in results_json:
                    if 'msm_id' in mini_json:
                        mini_json['msm id'] = mini_json['msm_id']
                    aux_var.append(mini_json)
                if len(aux_var) != len(results_json):
                    print 'Big ERROR'
                else:
                    results_json = aux_var
                if (len(results_json) == excpected_results or timedout):
                    response = requests.delete(URL_M)
                    if response.status_code != 204:
                        logging.info(str(chk_id) + response.content)
                    # if timedout:
                    #     print 'timedout : {}'.format(str(timedout))
                    try:
                        db.measurements.insert_one(measurement_json)
                        db.results.insert_many(results_json,
                                               ordered=False)
                        (db
                         .campaign_descriptor
                         .update_one({'msm_id': chk_id},
                                     {'$set':
                                     {'status': 'finished'}},
                                     upsert=False)
                         )
                    except DuplicateKeyError:
                        try:
                            db.results.insert_many(results_json,
                                                   ordered=False)
                            (db
                             .campaign_descriptor
                             .update_one({'msm_id': chk_id},
                                         {'$set':
                                         {'status': 'finished'}},
                                         upsert=False)
                             )
                        except DuplicateKeyError:
                                    (db
                                     .campaign_descriptor
                                     .update_one({'msm_id': chk_id},
                                                 {'$set':
                                                 {'status': 'finished'}},
                                                 upsert=False)
                                     )
                        except BulkWriteError as e:
                            logging.info(e.details)
                    except BulkWriteError as e:
                        logging.info(e.details)


def kill_all():
    URL_ONGOING = (
            'https://atlas.ripe.net/api/v2/measurements/my/?key={}&status=2'
            .format(ATLAS_API_KEY)
           )
    res = requests.get(URL_ONGOING)
    if res.status_code == 200:
        res = json.loads(res.content)
        print res
        for i in res['results']:
            print i['id']
            URL_M = (
                'https://atlas.ripe.net:443/api/v2/measurements/{}/?key={}'
                .format(str(i['id']), ATLAS_API_KEY)
            )
            res2 = requests.delete(URL_M)
            print res2.status_code
            print res2.content
