# -*- conding:utf-8 -*-
import json
import os

import oss2

from aliyunsdkcore import client
from aliyunsdkcore.profile import region_provider
from aliyunsdksts.request.v20150401 import AssumeRoleRequest

##定义一些变量
access_key_id = 'LTAI4FoMe6umpCSFQdEC9neg' 
access_key_secret = 'jgEvtFOqIAGqKZve7zMvg8dJhSZv9J'
bucket_name = 'fralychen'
endpoint = 'oss-cn-hongkong.aliyuncs.com'
sts_role_arn = 'acs:ram::1149877324567510:role/testrole'



# 确认上面的参数都填写正确了
for param in (access_key_id, access_key_secret, bucket_name, endpoint, sts_role_arn):
    assert '<' not in param, '请设置参数：' + param

#创建StsToken类方便用来存储临时用户信息
class StsInfo(object):
    """AssumeRole返回的临时用户密钥
    :param str access_key_id: 临时用户的access key id
    :param str access_key_secret: 临时用户的access key secret
    :param int expiration: 过期时间，UNIX时间，自1970年1月1日UTC零点的秒数
    :param str security_token: 临时用户Token
    :param str request_id: 请求ID
    """
    def __init__(self):
        self.access_key_id = ''
        self.access_key_secret = ''
        self.expiration = 0
        self.security_token = ''
        self.request_id = ''

# 在控制台将 AliyunSTSAssumeRoleAccess 权限授权给子用户testRole，testRole操作AssumeRole接口，获取临时用户信息
def fetch_sts_info(access_key_id, access_key_secret, sts_role_arn):
    """子用户角色扮演获取临时用户的密钥
    :param access_key_id: 子用户的 access key id
    :param access_key_secret: 子用户的 access key secret
    :param sts_role_arn: STS角色的Arn
    :return StsInfo 返回授权用户信息对象
    """
    # 配置要访问的STS endpoint
    _REGIONID = 'cn-hongkong'
    _ENDPOINT = 'sts.cn-hongkong.aliyuncs.com'
    region_provider.add_endpoint('Sts', _REGIONID, _ENDPOINT)

    clt = client.AcsClient(access_key_id, access_key_secret, 'cn-hongkong')
    request = AssumeRoleRequest.AssumeRoleRequest()

    #request.set_accept_format('json')
    #指定角色ARN
    request.set_RoleArn(sts_role_arn)
    #设置会话名称，审计服务使用此名称区分调用者
    request.set_RoleSessionName('oss-python-sdk-example')
    #设置临时身份过期时间
    request.set_DurationSeconds(DurationSeconds)
    #发起请求，并得到response
    response = clt.do_action_with_exception(request)
    #格式化输出返回结果，将字符串结果转化为字典类型
    i = json.loads(oss2.to_unicode(response))
    #实例化StsInfo类并将临时用户信息存入对象
    global StsInfo
    StsInfo = StsInfo()
    StsInfo.access_key_id = i['Credentials']['AccessKeyId']
    StsInfo.access_key_secret = i['Credentials']['AccessKeySecret']
    StsInfo.security_token = i['Credentials']['SecurityToken']
    StsInfo.request_id = i['RequestId']
    StsInfo.expiration = oss2.utils.to_unixtime(i['Credentials']['Expiration'], '%Y-%m-%dT%H:%M:%SZ')
    

    #存储临时用户信息
    save_info()


#使用sts授权的临时用户上传文件到bucket
def buck_put_object(sts_key_id, sts_key_secret, sts_secrity_token):
    """上传字符串到资源
    :param sts_key_id: 临时身份的 access key id
    :param sts_key_secret: 临时身份的 access key secret
    :param sts_secrity_token: 临时身份的 secrity token
    :retu
    """ 
    #实例化Bucket对象，并上传字符串
    auth = oss2.StsAuth(sts_key_id, sts_key_secret, sts_secrity_token)
    bucket = oss2.Bucket(auth,endpoint,'fralychen')
    result = bucket.put_object('fralychen','good good study day day up')

#根据需求，可将临时身份信息存储到json文件中，等到临时身份过期后再重新请求，避免重复请求，用户泛滥
def save_info():
    #存储临时身份信息
    with open('StsInfo.json','w',encoding='utf-8') as f:
        data = {'sts_key_id':StsInfo.access_key_id,'sts_key_secret':StsInfo.access_key_secret,'sts_secrity_token':StsInfo.security_token,'sts_expire_date':StsInfo.expiration,'sts_reques_id':StsInfo.request_id}
        json.dump(data,f,ensure_ascii=False)
        f.close


def open_info():
    #读取临时身份信息
    with open('./StsInfo.json','r',encoding='utf-8') as f:
        global STSINFO
        STSINFO = json.load(f)
        return STSINFO


#定义临时身份过期时间
DurationSeconds = 900

try:
    open_info()
except IOError:
    print("Error: 没有用户信息文件或文件读取失败")
    print("初始化身份信息，临时身份信息存储中....")
    fetch_sts_info(access_key_id, access_key_secret, sts_role_arn)
    print("临时身份信息存储完毕，当前目录下StsInfo.json")
else:
    if oss2.utils.http_to_unixtime(oss2.utils.http_date()) + DurationSeconds > STSINFO["sts_expire_date"]:
        buck_put_object(sts_key_id = STSINFO["sts_key_id"],sts_key_secret = STSINFO["sts_key_secret"], sts_secrity_token = STSINFO["sts_secrity_token"])
        print("上传成功，good_lucky")
    else:
        print("更新临时用户信息，请稍后")
        fetch_sts_info(access_key_id, access_key_secret, sts_role_arn)
        buck_put_object(sts_key_id = STSINFO["sts_key_id"],sts_key_secret = STSINFO["sts_key_secret"], sts_secrity_token = STSINFO["sts_secrity_token"])
        print("上传成功，good_lucky")


