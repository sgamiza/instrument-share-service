from core.json_object import JSONObject


def test_append_and_getitem():
    obj = JSONObject()
    obj.append_object("type", "sa")
    obj.append_object("json_config", {"k": 1})
    assert obj["type"] == "sa"
    assert obj.get_obj()[0] == {"type": "sa"}
    assert "sa" in obj.serialize()


def test_get_treats_falsy_as_missing():
    obj = JSONObject()
    obj.append_object("testing_duration", 0)
    assert obj.get("testing_duration", 99) == 99
    obj.append_object("mqtt_msg_id", "msg-1")
    assert obj.get("mqtt_msg_id", "fallback") == "msg-1"
