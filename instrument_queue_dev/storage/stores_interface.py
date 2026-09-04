# -*- coding: utf-8 -*-

import json
import time

from .stores import InstrumentStore


# class DeltaParameter(dict):
#
#     def __init__(self, name, value, operation="update"):
#         super(DeltaParameter, self).__init__(parameterName=name, value=value, operation=operation)
#
#     def __getattr__(self, attr):
#         return self.get(attr)
#
#     def __setattr__(self, attr, value):
#         self[attr] = value


# class DeltaManagedObject(object):
#
#     def __init__(self, dist_name, parameters=None):
#         if parameters is None:
#             parameters = {}
#         self.dist_name = dist_name
#         self.parameters = parameters
#
#     def serialize(self):
#         return {"distName": self.dist_name, "parameters": list(self.parameters.values())}
#
#     def append_parameter(self, parameter_name, value):
#         self.parameters[parameter_name] = DeltaParameter(parameter_name, value)



class JSONObject(dict):

    def __init__(self,*args, **kwargs):
        self.objects = {}
        super().__init__(*args, **kwargs)


    def __str__(self):
        return self.serialize()


    def __getitem__(self, object_name):
        # 方式1 不抛出异常
        # return self.objects[object_name] if self.objects.get(object_name) else None

        # 方式2 抛出异常
        try:
            return self.objects[object_name]
        except:
            raise


    def get(self ,k, d=None):
        # 2022-08-04 
        return self.objects[k] if self.objects.get(k) else d
        # 【常规dict】自己处理的逻辑,将自定义处理后的结果替换赋值给d即可
        # return self[k] if k in self else d


    def serialize(self):
        # return json.dumps([{"distName": k, "parameters": v}
        #                    for k,v in self.objects.values()], indent=4, separators=(',', ':'))
        return json.dumps([{k: v} for k,v in self.objects.items()], indent=4, separators=(',', ':'))


    def get_obj(self):
        return [{k: v} for k,v in self.objects.items()]


    def append_object(self, name, parameters=None):
        self.objects[name] = parameters



class ThreadingInterface(object):

    delta_store = InstrumentStore()

    @classmethod
    def create(cls, json_obj, id="default"):
        cls.delta_store.add(json_obj, id)

    @classmethod
    def get_all(cls, id="default"):
        return cls.delta_store.get(id).get_obj()

    @classmethod
    def get_serialized(cls, id="default"):
        return cls.delta_store.get(id).serialize()


    @classmethod
    def remove(cls, id="default"):
        cls.delta_store.remove(id)

    @classmethod
    def remove_all(cls):
        cls.delta_store.reset()


# def _test(arg):
#     time.sleep(1)
#     print("test job %s running.."%arg)


# TODO 删除 __main__
if __name__ == '__main__':

    res = JSONObject()

    # thread demo
    # thread = threading.Thread(target=_test, args=("test_str",))
    # thread.start()
    # # thread.join() # 【重点】指定这个 thread 线程优先执行完毕
    #
    # res.append_object(name="test", parameters={"testKey": "testvalue"})
    # res.append_object(name="127.0.0.1", parameters=thread)
    #
    # ti = ThreadingInterface()
    # ti.create(res)
    # print(ti.get_all())


    # JSONObject demo
    res.append_object(name="test", parameters={"testKey": "testvalue"})
    res.append_object(name="127.0.0.1", parameters="test")

    print(res.objects["test"]) # 方式1
    print(res["test"]) # 方式2
    # print(res["test1"]) # 异常 或者 None





