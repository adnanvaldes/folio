expected_data = {
    "dict": {
        "simple": {
            "int_field": 1,
            "string_field": "a string",
            "bool_field": False,
            "float_field": 2.0,
        },
        "with_none": {
            "int_field": 2,
            "string_field": "test2",
            "bool_field": True,
            "float_field": None,
        },
        "complex": {
            "list_field": ["a", "b", "c"],
            "dict_field": {"a": 1, "b": "some string", "c": ["a list"]},
            "none_default_field": None,
        },
        "empty": {},
        "extra": {
            "int_field": 2,
            "string_field": "test2",
            "bool_field": True,
            "float_field": None,
            "extra_field": "extra data",
        },
    },
    "json": {
        "simple": (
            '{"int_field": 1, "string_field": "a string", '
            '"bool_field": false, "float_field": 2.0}'
        ),
        "with_none": (
            '{"int_field": 2, "string_field": "test2", '
            '"bool_field": true, "float_field": null}'
        ),
        "complex": (
            '{"list_field": ["a", "b", "c"], '
            '"dict_field": {"a": 1, "b": "some string", "c": ["a list"]}, '
            '"none_default_field": null}'
        ),
        "empty": "{}",
        "extra": (
            '{"int_field": 2, "string_field": "test2", '
            '"bool_field": true, "float_field": null, '
            '"extra_field": "extra data"}'
        ),
    },
    "xml": {
        "simple": (
            "<SampleRecord>"
            "<int_field>1</int_field>"
            "<string_field>a string</string_field>"
            "<bool_field>false</bool_field>"
            "<float_field>2.0</float_field>"
            "</SampleRecord>"
        ),
        "with_none": (
            "<SampleRecord>"
            "<int_field>2</int_field>"
            "<string_field>test2</string_field>"
            "<bool_field>true</bool_field>"
            "<float_field/>"
            "</SampleRecord>"
        ),
        "complex": (
            "<ComplexSampleRecord>"
            "<list_field><item>a</item><item>b</item><item>c</item></list_field>"
            "<dict_field>"
            "<a>1</a><b>some string</b><c><item>a list</item></c>"
            "</dict_field>"
            "<none_default_field/>"
            "</ComplexSampleRecord>"
        ),
        "empty": "<EmptySampleRecord/>",
        "extra": (
            "<SampleRecord>"
            "<int_field>2</int_field>"
            "<string_field>test2</string_field>"
            "<bool_field>true</bool_field>"
            "<float_field/>"
            "<extra_field>extra data</extra_field>"
            "</SampleRecord>"
        ),
    },
}
