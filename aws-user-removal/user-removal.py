from datetime import datetime, timedelta
from typing import Dict
​
import boto3
from dateutil.tz import tzutc
from pip import main
​
​
def check_users_last_login(
        client,
        inactivate_period:int = 45, 
        delete_period:int = 90) -> list :
    
        """
        This fucntion check last login from users from console and using Access key and return thos users who didn't any activity during inactivate_period(default 
        is 45 days) days as inactive_users and also thos users who didn't any activity during delete_period(default is 90 days) days as delete_users
        Arguments:
            client {} ==> Boto3 client 
            inactivate_period: {int} ==> inactivation period
            delete_period: {int} ==> inactivation period            
        """
​
​
        create_under_activation_boundary=datetime.now() - timedelta(inactivate_period)
        for user in client.list_users()['Users']:
            if (create_under_activation_boundary > user["CreateDate"].replace(tzinfo=None)):
                users[user["UserName"]]=user
​
        inactive_users=[]
        delete_users=[]
​
        inactive_date_boundary=datetime.now() - timedelta(inactivate_period)
        delete_date_boundary=datetime.now() - timedelta(delete_period)
​
        for user in users.keys():
            
            user_keys = client.list_access_keys(
                UserName=user,
                MaxItems=10)
            
            if "PasswordLastUsed" in users[user].keys():
                last_used_date=users[user]["PasswordLastUsed"].replace(tzinfo=None)
            else:
                last_used_date=users[user]["CreateDate"].replace(tzinfo=None)
            
            if 'AccessKeyMetadata' in user_keys:
                for key in user_keys['AccessKeyMetadata']:
                    if 'AccessKeyId' in key:
                        access_key_id = key['AccessKeyId']
                        res_last_used_key = client.get_access_key_last_used( \
                                          AccessKeyId=access_key_id)
​
                        if ('LastUsedDate' in res_last_used_key["AccessKeyLastUsed"]) and \
                           (res_last_used_key['AccessKeyLastUsed']['LastUsedDate'].replace(tzinfo=None) > last_used_date):
                           
                            last_used_date = res_last_used_key['AccessKeyLastUsed']['LastUsedDate'].replace(tzinfo=None)
​
            if (delete_date_boundary>last_used_date):
                delete_users.append(user)
​
            elif (inactive_date_boundary >last_used_date):
                inactive_users.append(user)
        
        return [inactive_users, delete_users]
​
​
def inactive_user(client, inactive_users:set=None):
​
    """
      This function disabling user authentication using console 
       Arguments:
            client {} ==> Boto3 client 
            inactive_users: {set} ==> a set including of inactive users 
    """
    try: 
            
        for user in inactive_users:
            client.delete_login_profile(UserName=user) # disabling login from console 
    except Exception as e:
        print(e)
​
​
if __name__ == '__main__':
    users={}
    client = boto3.client('iam')
    whitelist={"awsKyryl", "awsPowerBIAthena","awsQAGenerator","ccnaDev","ccnaProd","client-cc-aunz", "client-ccep-be","client-ccep-de","client-ccep-es", \
                   "client-ccep-nl","client-ccep-pt", "client-ccna-us","client-heineken-dk","client-heineken-pt","client-ko-global","client.app"\
                   ,"financeAWS","github.actions", ""}
    
    deactive_users, delete_users=check_users_last_login(client)
​
    final_deactive_users=set(deactive_users).difference(whitelist)
    final_delete_users=set(delete_users).difference(whitelist)
    inactive_user(client, final_deactive_users)
    inactive_user(final_delete_users)
    print(final_deactive_users)