def test_aliyun_void():
    from iris.vendors.iris_aliyun import iris_aliyun
    voice = iris_aliyun({
        'access_key_id': '',
        'access_secret': '',
        'region': '',
        'number': '',
        'tts_code': '',
    })
    resp = voice.send_call({})
    print(resp)
