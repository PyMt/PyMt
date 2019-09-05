# -*- conding:utf-8 -*-
import json
import os

import oss2

from aliyunsdkcore import client
from aliyunsdkcore.profile import region_provider
from aliyunsdksts.request.v20150401 import AssumeRoleRequest

##定义一些变量
access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', '<yourAccessKeyId>')
access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', '<yourAccessKeySecret>')
bucket_name = os.getenv('OSS_TEST_BUCKET', '<yourBucket>')
endpoint = os.getenv('OSS_TEST_ENDPOINT', '<yourEndpoint>')
sts_role_arn = os.getenv('STS_ROLE_ARN', '<yourStsRoleArn>')


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
    REGIONID = 'cn-hongkong'
    ENDPOINT = 'sts.cn-hongkong.aliyuncs.com'
    region_provider.add_endpoint('Sts', REGIONID, ENDPOINT)

    clt = client.AcsClient(access_key_id, access_key_secret, 'cn-hongkong')
    request = AssumeRoleRequest.AssumeRoleRequest()

    #request.set_accept_format('json')
    #指定角色ARN
    request.set_RoleArn(sts_role_arn)
    #设置会话名称，审计服务使用此名称区分调用者
    request.set_RoleSessionName('oss-python-sdk-example')
    #发起请求，并得到response
    response = clt.do_action_with_exception(request)
    #格式化输出返回结果，将字符串结果转化为字典类型
    i = json.loads(oss2.to_unicode(response))
    #实例化StsInfo类并将通过sts获取的临时用户信息存入
    global StsInfo
    StsInfo = StsInfo()
    StsInfo.access_key_id = i['Credentials']['AccessKeyId']
    StsInfo.access_key_secret = i['Credentials']['AccessKeySecret']
    StsInfo.security_token = i['Credentials']['SecurityToken']
    StsInfo.request_id = i['RequestId']
    StsInfo.expiration = oss2.utils.to_unixtime(i['Credentials']['Expiration'], '%Y-%m-%dT%H:%M:%SZ')

    #返回StsInfo对象
    return StsInfo



#使用sts授权的临时用户上传文件到bucket
def buck_put_object():
    #打印验证sts授权的临时用户信息
    print(StsInfo)
    print('key id:',StsInfo.access_key_id)
    print("key_secret:",StsInfo.access_key_secret)
    print("secrity_token:",StsInfo.security_token)
    print("request_id:",StsInfo.request_id)
    print("expiration:",StsInfo.expiration)
    
    #实例化Bucket对象，并上传字符串
    auth = oss2.StsAuth(StsInfo.access_key_id, StsInfo.access_key_secret, StsInfo.security_token)
    bucket = oss2.Bucket(auth,endpoint,'fralychen')
    result = bucket.put_object('fralychen','good good study day day up')

if __name__ == "__main__":
    fetch_sts_info(access_key_id, access_key_secret, sts_role_arn)
    buck_put_object()