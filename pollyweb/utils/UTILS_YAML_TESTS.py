# 📚 YAML


from .UTILS_YAML import UTILS_YAML
from .TESTS import TESTS
from .STRUCT import STRUCT
from .TESTS import ValidationException



# ✅ DONE
class UTILS_YAML_TESTS(UTILS_YAML):


    @classmethod
    def TestFromJson(cls):
        TESTS.AssertEquals([
            [cls.FromJson('{"a": 1, "b": 2}'), {'a':1,'b':2}],
            [cls.FromJson('{"a": true}'), {"a":True}],
        ])
        
    
    @classmethod
    def TestToJson(cls):
        
        # Convert bytes.
        cls.ToJson(b'a')
        cls.ToJson({'x': b'a'})

        TESTS.AssertEquals([
            [cls.ToJson({"a":1}), '{"a": 1}'],
            [cls.ToJson({"a":True}), '{"a": true}'],
            [cls.ToJson({"a":"x"}), '{"a": "x"}']
        ])
    
    
    @classmethod
    def TestFromYaml(cls):
        yaml = "products:\n  - item 1\n  - item 2\n"
        obj = {'products':['item 1', 'item 2']}
        TESTS.AssertEqual(cls.FromYaml(yaml), obj)
    

    @classmethod
    def TestFromYamlRejectsUnsafeTags(cls):
        payload = "a: !!python/object/apply:os.system ['echo hacked']"
        with TESTS.AssertValidation(type=ValidationException):
            cls.FromYaml(payload)
        
        
    @classmethod
    def TestToYaml(cls):
        yaml = "products:\n  - item 1\n  - item 2"
        obj = {'products':['item 1', 'item 2']}
        TESTS.AssertEquals([
            [cls.ToYaml(obj), yaml],
            [cls.ToYaml(STRUCT(obj)), yaml]
        ])


    @classmethod
    def TestFromJsonToYaml(cls):
        yaml = "products:\n  - item 1\n  - item 2"
        obj = {'products':['item 1', 'item 2']}
        json = cls.ToJson(obj)
        TESTS.AssertEqual(
            given= cls.FromJsonToYaml(json), 
            expect= yaml
        )
        
        
    @classmethod
    def TestFromYamlToJson(cls):
        yaml = "products:\n  - item 1\n  - item 2\n"
        obj = {'products':['item 1', 'item 2']}
        json = cls.ToJson(obj)
        TESTS.AssertEqual(
            given= cls.FromYamlToJson(yaml), 
            expect= json
        )
    

    @classmethod
    def TestAllYaml(cls):
        cls.TestFromJson()
        cls.TestToJson()
        cls.TestFromYaml()
        cls.TestFromYamlRejectsUnsafeTags()
        cls.TestToYaml()
        cls.TestFromJsonToYaml()
        cls.TestFromYamlToJson()
