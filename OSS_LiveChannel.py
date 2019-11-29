#coding=utf-8                                                                                                                                                                                                       import os
import time
import oss2

access_key_id= ''
access_key_secret= ''

bucket_name = 'fralychen'

#endpoint = 'oss-cn-hongkong.aliyuncs.com'
endpoint = 'oss-cn-beijing.aliyuncs.com'

#初始化bucket
bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)


#创建LiveChannel
channel_name = 'test_rtmp_live'
playlist_name = 'test.m3u8'
create_result = bucket.create_live_channel(
                channel_name,
                oss2.models.LiveChannelInfo(
                                status = 'enabled',
                                            description = '测试使用的直播频道',
                                            target = oss2.models.LiveChannelInfoTarget(
                                                                playlist_name = playlist_name,
                                                                                frag_count = 3,
                                                                                                frag_duration = 5
                                                )
                    )
        )
#获取推流观流地址
publish_url = create_result.publish_url
play_url = create_result.play_url
print("推流地址:",publish_url)
print("观流地址:",play_url)
'推流地址: rtmp://***-channel.oss-cn-***.aliyuncs.com/**/**-**'
'观流地址: http://***-channel.oss-cn-****.aliyuncs.com/song-**/**.m3u8'

prefix = ''
max_keys = 1000

#for info in oss2.LiveChannelIterator(bucket, prefix, max_keys=max_keys):
for info in oss2.LiveChannelIterator(bucket):
    print(info.name)

bucket.delete_live_channel(info.name)


#查看当前流的状态信息状态
get_statu = bucket.get_live_channel_stat(info.name)
print("连接时间:",get_statu.connected_time)
print("推流客户端的IP:",get_statu.remote_addr )
print("推流状态:",get_statu.status )


#查看LiveChannel配置信息
get_result = bucket.get_live_channel(info.name)
print("-------------------")
print("推流配置信息:")
print(get_result.description)
print(get_result.status)
print(get_result.target.type)
print(get_result.target.frag_count)
print(get_result.target.frag_duration)
print(get_result.target.playlist_name)
print("-------------------")


# 拿到推流地址和观流地址之后就可以向OSS推流和观流。如果Bucket的权限不是公共读写，那么还需要对推流做签名，如果Bucket是公共读写的，那么可以直接用publish_url推流。
# 这里的expires是一个相对时间，指的是从现在开始这次推流过期的秒数。
# params是一个dict类型的参数，表示用户自定义的参数。所有的参数都会参与签名。
# 拿到这个签过名的signed_url就可以使用推流工具直接进行推流，一旦连接上OSS之后超过上面的expires流也不会断掉，OSS仅在每次推流连接的时候检查expires是否合法。
signed_url = bucket.sign_rtmp_url(channel_name, playlist_name, expires=3600)
print(signed_url)



end_time = int(time.time()) - 60
start_time = end_time - 3600
bucket.post_vod_playlist(channel_name, playlist_name=playlist_name, start_time=start_time, end_time=end_time)

# 如果想查看指定时间段内的播放列表，可以使用get_vod_playlist
result = bucket.get_vod_playlist(channel_name, start_time=start_time, end_time=end_time)
print("playlist:", result.playlist)


# 查看一个频道历史推流记录，可以调用get_live_channel_history目前最多可以看到10次推流的记录
history_result = bucket.get_live_channel_history(channel_name)
print("推流历史次数:",len(history_result.records))
