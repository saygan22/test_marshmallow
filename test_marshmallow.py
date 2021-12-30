from pprint import pprint

import pytest
from invenio_records_rest.schemas.fields import SanitizedUnicode
from marshmallow import ValidationError, Schema
from marshmallow.fields import Nested, List
from sqlalchemy.orm.exc import NoResultFound

from oarepo_taxonomies.marshmallow import TaxonomySchema, extract_link, get_slug_from_link, \
    TaxonomyField, TaxonomyNested


def test_resolve_links_random():
    """
    Test if random user data are passed.
    """
    random_user_data = {
        "created_at": "2014-08-11T05:26:03.869245",
        "email": "ken@yahoo.com",
        "name": "Ken",
        "test": "bla"
    }
    schema = TaxonomySchema()
    with pytest.raises(ValidationError):
        schema.load(random_user_data)


def test_resolve_links_random_link(taxonomy_tree):
    """
    Test if random user data with link resolve taxonomy and keep user data.
    """
    random_user_data = {
        "created_at": "2014-08-11T05:26:03.869245",
        "email": "ken@yahoo.com",
        "name": "Ken",
        "links": {
            "self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b"
        }
    }
    schema = TaxonomySchema()
    res = schema.load(random_user_data)
    # pprint(res)
    assert res == [{
        'is_ancestor': True,
        'level': 1,
        'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a'},
        'test': 'extra_data'
    },
        {
            'created_at': '2014-08-11T05:26:03.869245',
            'email': 'ken@yahoo.com',
            'is_ancestor': False,
            'level': 2,
            'links': {
                'parent': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a',
                'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b'
            },
            'name': 'Ken',
            'test': 'extra_data'
        }]


def test_resolve_links_random_string(app, db, taxonomy_tree):
    """
    Test if random user data (string) are passed.
    """
    random_user_data = "bla bla http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b"
    schema = TaxonomySchema()
    result = schema.load(random_user_data)
    # pprint(result)
    assert result == [{
        'is_ancestor': True,
        'level': 1,
        'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a'},
        'test': 'extra_data'
    },
        {
            'is_ancestor': False,
            'level': 2,
            'links': {
                'parent': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a',
                'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b'
            },
            'test': 'extra_data'
        }]


def test_resolve_links_random_string_2(app, db, taxonomy_tree):
    """
    Test if wrong url (string) does not pass.
    """
    random_user_data = "bla bla http://example.com/"
    schema = TaxonomySchema()
    with pytest.raises(ValueError):
        schema.load(random_user_data)


def test_resolve_links_random_string_3(app, db, taxonomy_tree):
    """
    Test if wrong url (string) does not pass.
    """
    random_user_data = "bla bla http://example.com/taxonomies/a/b/z"
    schema = TaxonomySchema()
    with pytest.raises(ValidationError, match="Taxonomy term 'a/b/z' has not been found"):
        schema.load(random_user_data)


def test_resolve_links_random_string_4(app, db, taxonomy_tree):
    """
    Test if random user data (string) are passed.
    """
    random_user_data = "bla bla http://example.com/a/b/z"
    schema = TaxonomySchema()
    with pytest.raises(ValueError):
        schema.load(random_user_data)


def test_resolve_links_array(app, db, taxonomy_tree):
    """
    Test if random user data (string) are passed.
    """
    random_user_data = [
        {
            'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a'},
        },
        {
            'links': {
                'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b'
            },
            'test': 'extra_data',
            'next': 'bla',
            'another': 'something'
        }
    ]
    schema = TaxonomySchema(many=True)
    result = schema.load(random_user_data)
    # pprint(result)
    assert result == [{
        'is_ancestor': True,
        'level': 1,
        'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a'},
        'test': 'extra_data'
    },
        {
            'another': 'something',
            'is_ancestor': False,
            'level': 2,
            'links': {
                'parent': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a',
                'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b'
            },
            'next': 'bla',
            'test': 'extra_data'
        }]


def test_nested_schema(app, db, taxonomy_tree):
    class TestSchema(Schema):
        field = TaxonomyField()

    random_user_taxonomy = {
        "created_at": "2014-08-11T05:26:03.869245",
        "email": "ken@yahoo.com",
        "name": "Ken",
        "links": {
            "self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b"
        }
    }

    data = {
        "field": random_user_taxonomy
    }

    schema = TestSchema()
    result = schema.load(data)
    assert result == {
        'field': [{
            'is_ancestor': True,
            'level': 1,
            'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a'},
            'test': 'extra_data'
        },
            {
                'created_at': '2014-08-11T05:26:03.869245',
                'email': 'ken@yahoo.com',
                'is_ancestor': False,
                'level': 2,
                'links': {
                    'parent': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a',
                    'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b'
                },
                'name': 'Ken',
                'test': 'extra_data'
            }]
    }


def test_nested_schema_2(app, db, taxonomy_tree):
    class TestSchema(Schema):
        field = TaxonomyField(many=True)

    random_user_taxonomy = [
        {
            'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a'},
        },
        {
            'links': {
                'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b'
            },
            'test': 'extra_data',
            'next': 'bla',
            'another': 'something'
        }
    ]

    data = {
        "field": random_user_taxonomy
    }

    schema = TestSchema()
    result = schema.load(data)
    # pprint(result)
    assert result == {
        'field': [{
            'is_ancestor': True,
            'level': 1,
            'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a'},
            'test': 'extra_data'
        },
            {
                'another': 'something',
                'is_ancestor': False,
                'level': 2,
                'links': {
                    'parent': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a',
                    'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b'
                },
                'next': 'bla',
                'test': 'extra_data'
            }]
    }


@pytest.mark.skip(reason="marshmallow.List isn't working yet")
def test_nested_schema_3(app, db, taxonomy_tree):
    class TestSchema(Schema):
        field = List(Nested(TaxonomySchema()))

    random_user_taxonomy = [
        {
            'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a'},
        },
        {
            'links': {
                'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b'
            },
            'test': 'extra_data',
            'next': 'bla',
            'another': 'something'
        }
    ]

    data = {
        "field": random_user_taxonomy
    }

    schema = TestSchema()
    result = schema.load(data)
    assert result == {
        'field': [{
            'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a'},
            'test': 'extra_data'
        },
            {
                'another': 'something',
                'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b'},
                'next': 'bla',
                'test': 'extra_data'
            }]
    }


def test_nested_schema_4(app, db, taxonomy_tree):
    class TestSchema(Schema):
        field = TaxonomyField(many=False)

    random_user_taxonomy = "bla bla http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b"

    data = {
        "field": random_user_taxonomy
    }

    schema = TestSchema()
    result = schema.load(data)
    # pprint(result)
    assert result == {
        'field': [{
            'is_ancestor': True,
            'level': 1,
            'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a'},
            'test': 'extra_data'
        },
            {
                'is_ancestor': False,
                'level': 2,
                'links': {
                    'parent': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a',
                    'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b'
                },
                'test': 'extra_data'
            }]
    }


def test_extract_link_1():
    url = extract_link("bla bla http://example.com/")
    assert url == "http://example.com/"


def test_extract_link_2():
    url = extract_link("bla bla")
    assert url is None


def test_get_slug_from_link():
    slug, code = get_slug_from_link("http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b")
    assert slug == "a/b"
    assert code == "test_taxonomy"


def test_taxonomy_field():
    extra = {
        "title": SanitizedUnicode(required=False),
        "language": List(SanitizedUnicode(required=False))
    }
    schema = TaxonomyField(extra=extra, name="taxonomy")
    assert type(schema) == TaxonomyNested
    assert "title" in schema.nested.fields.keys()
    assert "language" in schema.nested.fields.keys()


def test_taxonomy_field_mixin(app, db, taxonomy_tree):
    class InstitutionMixin:
        name = SanitizedUnicode()
        address = SanitizedUnicode()

    class TestSchema(Schema):
        field = TaxonomyField(many=True, mixins=[InstitutionMixin])

    random_user_taxonomy = [
        {
            'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a'},
        },
        {
            'links': {
                'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b'
            },
            'test': 'extra_data',
            'next': 'bla',
            'another': 'something',
            'name': 'Hogwarts',
            'address': 'Platform nine and three-quarters'
        }
    ]

    data = {
        "field": random_user_taxonomy
    }

    schema = TestSchema()
    result = schema.load(data)
    pprint(result)
    assert result == {
        'field': [{
                      'is_ancestor': True,
                      'level': 1,
                      'links': {'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a'},
                      'test': 'extra_data'
                  },
                  {
                      'address': 'Platform nine and three-quarters',
                      'another': 'something',
                      'is_ancestor': False,
                      'level': 2,
                      'links': {
                          'parent': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a',
                          'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/a/b'
                      },
                      'name': 'Hogwarts',
                      'next': 'bla',
                      'test': 'extra_data'
                  }]
    }