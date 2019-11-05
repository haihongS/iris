
def test_dingding():
    from iris.vendors.iris_dingding import iris_dingding
    dingding = iris_dingding({
        'base_url': 'xx',
    })
    dingding.send_dingding({})
