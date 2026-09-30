# Pydantic V2 Migration Guide (selected sections)

Source: https://raw.githubusercontent.com/pydantic/pydantic/v2.0/docs/migration.md (verbatim excerpt, fetched 2026-09-29)
License: Pydantic documentation, MIT License (https://github.com/pydantic/pydantic). Verbatim excerpt.

Pydantic 2.0 was released on 2023-06-30. Sections are cut programmatically from the guide's "Migration guide" chapter; headings keep their original levels.

---

### Changes to `pydantic.BaseModel`

Various method names have been changed; all non-deprecated `BaseModel` methods now have names matching either the
format `model_.*` or `__.*pydantic.*__`. Where possible, we have retained the deprecated methods with their old names
to help ease migration, but calling them will emit `DeprecationWarning`s.

| Pydantic V1 | Pydantic V2  |
| ----------- | ------------ |
| `__fields__` | `model_fields` |
| `__private_attributes__` | `__pydantic_private__` |
| `__validators__` | `__pydantic_validator__` |
| `construct()` | `model_construct()` |
| `copy()` | `model_copy()` |
| `dict()` | `model_dump()` |
| `json_schema()` | `model_json_schema()` |
| `json()` | `model_dump_json()` |
| `parse_obj()` | `model_validate()` |

* Some of the built-in data-loading functionality has been slated for removal. In particular,
    `parse_raw` and `parse_file` are now deprecated. In Pydantic V2, `model_validate_json` works like `parse_raw`. Otherwise, you should load the data and then pass it to `model_validate`.
* The `from_orm` method has been deprecated; you can now just use `model_validate` (equivalent to `parse_obj` from
  Pydantic V1) to achieve something similar, as long as you've set `from_attributes=True` in the model config.
* The `__eq__` method has changed for models.
    * Models can only be equal to other `BaseModel` instances.
    * For two model instances to be equal, they must have the same:
        * Type (or, in the case of generic models, non-parametrized generic origin type)
        * Field values
        * Extra values (only relevant when `model_config['extra'] == 'allow'`)
        * Private attribute values; models with different values of private attributes are no longer equal.
        * Models are no longer equal to the dicts containing their data.
        * Non-generic models of different types are never equal.
        * Generic models with different origin types are never equal. We don't require *exact* type equality so that,
            for example, instances of `MyGenericModel[Any]` could be equal to instances of `MyGenericModel[int]`.
* We have replaced the use of the `__root__` field to specify a "custom root model" with a new type called
    [`RootModel`](usage/models.md#rootmodel-and-custom-root-types) which is intended to replace the functionality of
    using a field called `__root__` in Pydantic V1.
* We have significantly expanded Pydantic's capabilities related to customizing serialization. In particular, we have
    added the [`@field_serializer`](api/functional_serializers.md#pydantic.functional_serializers.field_serializer),
    [`@model_serializer`](api/functional_serializers.md#pydantic.functional_serializers.model_serializer), and
    [`@computed_field`](api/fields.md#pydantic.fields.computed_field) decorators, which each address various
    shortcomings from Pydantic V1.
    * See [Custom serializers](usage/serialization.md#custom-serializers) for the usage docs of these new decorators.
    * Due to performance overhead and implementation complexity, we have now removed support for specifying
        `json_encoders` in the model config. This functionality was originally added for the purpose of achieving custom
        serialization logic, and we think the new serialization decorators are a better choice in most common scenarios.
        However, if your usage of `json_encoders` is not compatible with the new serialization decorators,
        please create a GitHub issue letting us know. See [Custom data types](usage/types/custom.md) for further
        details.
* We have changed the behavior related to serializing subclasses of models when they occur as nested fields in a parent
  model. In V1, we would always include all fields from the subclass instance. In V2, when we dump a model, we only
  include the fields that are defined on the annotated type of the field. This helps prevent some accidental security
  bugs. You can read more about this (including how to opt out of this behavior) in the
  [Subclass instances for fields of BaseModel, dataclasses, TypedDict](usage/serialization.md#subclass-instances-for-fields-of-basemodel-dataclasses-typeddict)
  section of the model exporting docs.
* `GetterDict` has been removed as it was just an implementation detail of `orm_mode`, which has been removed.

### Changes to `pydantic.Field`

`Field` no longer supports arbitrary keyword arguments to be added to the JSON schema. Instead, any extra
data you want to add to the JSON schema should be passed as a dictionary to the `json_schema_extra` keyword argument.

The following properties have been removed from or changed in `Field`:

- `const`
- `min_items` (use `min_length` instead)
- `max_items` (use `max_length` instead)
- `unique_items`
- `allow_mutation` (use `frozen` instead)
- `regex` (use `pattern` instead)
- `final` (use the `typing.Final` type hint instead)

* [TODO: Need to document any other backwards-incompatible changes to `pydantic.Field`]

### Changes to config

* In Pydantic V2, to specify config on a model, you should set a class attribute called `model_config` to be a dict
  with the key/value pairs you want to be used as the config. The Pydantic V1 behavior to create a class called `Config`
  in the namespace of the parent `BaseModel` subclass is now deprecated.

* The following config settings have been removed:
    * `allow_mutation` — this has been removed. You should be able to use [frozen](api/config.md#pydantic.config.ConfigDict) equivalently (inverse of current use).
    * `error_msg_templates`.
    * `fields` — this was the source of various bugs, so has been removed.
      You should be able to use `Annotated` on fields to modify them as desired.
    * `getter_dict` — `orm_mode` has been removed, and this implementation detail is no longer necessary.
    * `smart_union`.
    * `underscore_attrs_are_private` — the Pydantic V2 behavior is now the same as if this was always set
      to `True` in Pydantic V1.

* The following config settings have been renamed:
    * `allow_population_by_field_name` → `populate_by_name`
    * `anystr_lower` → `str_to_lower`
    * `anystr_strip_whitespace` → `str_strip_whitespace`
    * `anystr_upper` → `str_to_upper`
    * `keep_untouched` → `ignored_types`
    * `max_anystr_length` → `str_max_length`
    * `min_anystr_length` → `str_min_length`
    * `orm_mode` → `from_attributes`
    * `schema_extra` → `json_schema_extra`
    * `validate_all` → `validate_default`

See [Model Config](usage/model_config.md) for more details.

### Changes to validators

#### `@validator` and `@root_validator` are deprecated

* `@validator` has been deprecated, and should be replaced with [`@field_validator`](usage/validators.md), which provides various new features
    and improvements.
    * The new `@field_validator` decorator does not have the `each_item` keyword argument; validators you want to
        apply to items within a generic container should be added by annotating the type argument. See
        [validators in Annotated metadata](usage/validators.md#generic-validated-collections) for details.
        This looks like `List[Annotated[int, Field(ge=0)]]`
    * Even if you keep using the deprecated `@validator` decorator, you can no longer add the `field` or
        `config` arguments to the signature of validator functions. If you need access to these, you'll need
        to migrate to `@field_validator` — see the [next section](#changes-to-validators-allowed-signatures)
        for more details.
    * If you use the `always=True` keyword argument to a validator function, note that standard validators
        for the annotated type will _also_ be applied even to defaults, not just the custom validators. For
        example, despite the fact that the validator below will never error, the following code raises a `ValidationError`:

```python test="skip"
from pydantic import BaseModel, validator


class Model(BaseModel):
    x: str = 1

    @validator('x', always=True)
    @classmethod
    def validate_x(cls, v):
        return v


Model()
```

* `@root_validator` has been deprecated, and should be replaced with
    [`@model_validator`](api/functional_validators.md#pydantic.functional_validators.model_validator), which also provides new features and improvements.
    * Under some circumstances (such as assignment when `model_config['validate_assignment'] is True`),
        the `@model_validator` decorator will receive an instance of the model, not a dict of values. You may
        need to be careful to handle this case.
    * Even if you keep using the deprecated `@root_validator` decorator, due to refactors in validation logic,
        you can no longer run with `skip_on_failure=False` (which is the default value of this keyword argument,
        so must be set explicitly to `True`).

#### Changes to `@validator`'s allowed signatures

In Pydantic V1, functions wrapped by `@validator` could receive keyword arguments with metadata about what was
being validated. Some of these arguments have been removed from `@field_validator` in Pydantic V2:

* `config`: Pydantic V2's config is now a dictionary instead of a class, which means this argument is no longer
    backwards compatible. If you need to access the configuration you should migrate to `@field_validator` and use
    `info.config`.
* `field`: this argument used to be a `ModelField` object, which was a quasi-internal class that no longer exists
    in Pydantic V2. Most of this information can still be accessed by using the field name from `info.field_name`
    to index into `cls.model_fields`

```python
from pydantic import BaseModel, FieldValidationInfo, field_validator


class Model(BaseModel):
    x: int

    @field_validator('x')
    def val_x(cls, v: int, info: FieldValidationInfo) -> int:
        assert info.config is not None
        print(info.config.get('title'))
        #> Model
        print(cls.model_fields[info.field_name].is_required())
        #> True
        return v


Model(x=1)
```

#### `TypeError` is no longer converted to `ValidationError` in validators

Previously, when raising a `TypeError` within a validator function, that error would be wrapped into a `ValidationError`
and, in some cases (such as with FastAPI), these errors might be displayed to end users. This led to a variety of
undesirable behavior &mdash; for example, calling a function with the wrong signature might produce a user-facing
`ValidationError`.

However, in Pydantic V2, when a `TypeError` is raised in a validator, it is no longer converted into a
`ValidationError`:

```python
import pytest

from pydantic import BaseModel, field_validator  # or validator


class Model(BaseModel):
    x: int

    @field_validator('x')
    def val_x(cls, v: int) -> int:
        return str.lower(v)  # raises a TypeError


with pytest.raises(TypeError):
    Model(x=1)
```

This applies to all validation decorators.

#### Validator behavior changes

Pydantic V2 includes some changes to type coercion. For example:

* int, float, and decimal values are no longer coerced to strings.
* iterable of pairs is no longer coerced to a dict.

See the [Conversion table](usage/conversion_table.md) for details on Pydantic V2 type coercion defaults.

#### The `allow_reuse` keyword argument is no longer necessary

Previously, Pydantic tracked "reused" functions in decorators as this was a common source of mistakes.
We did this by comparing the function's fully qualified name (module name + function name), which could result in false
positives. The `allow_reuse` keyword argument could be used to disable this when it was intentional.

Our approach to detecting repeatedly defined functions has been overhauled to only error for redefinition within a
single class, reducing false positives and bringing the behavior more in line with the errors that type checkers
and linters would give for defining a method with the same name multiple times in a single class definition.

In nearly all cases, if you were using `allow_reuse=True`, you should be able to simply delete that keyword argument and
have things keep working as expected.

#### Required, optional, and nullable fields

Pydantic V1 had a somewhat loose idea about "required" versus "nullable" fields. In Pydantic V2, these concepts are
more clearly defined.

Pydantic V2 will move to match `dataclasses`, thus you may explicitly specify a field as `required` or `optional` and whether the field accepts `None` or not.

```py
from typing import Optional

from pydantic import BaseModel, ValidationError


class Foo(BaseModel):
    f1: str  # required, cannot be None
    f2: Optional[str]  # required, can be None - same as str | None
    f3: Optional[str] = None  # not required, can be None
    f4: str = 'Foobar'  # not required, but cannot be None


try:
    Foo(f1=None, f2=None, f4='b')
except ValidationError as e:
    print(e)
    """
    1 validation error for Foo
    f1
      Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    """
```

### Introduction of `TypeAdapter`

Pydantic V1 had weak support for validating or serializing non-`BaseModel` types.

To work with them, you had to either create a "root" model or use the utility functions in `pydantic.tools`
(namely, `parse_obj_as` and `schema_of`).

In Pydantic V2 this is _a lot_ easier: the `TypeAdapter` class lets you create an object with methods for validating,
serializing, and producing JSON schemas for arbitrary types. This serves as a complete replacement for `parse_obj_as`
and `schema_of` (which are now deprecated), and also covers some of the use cases of "root" models
(`RootModel`, discussed above, covers the others).

```python
from typing import List

from pydantic import TypeAdapter

adapter = TypeAdapter(List[int])
assert adapter.validate_python(['1', '2', '3']) == [1, 2, 3]
print(adapter.json_schema())
#> {'items': {'type': 'integer'}, 'type': 'array'}
```

Due to limitations of inferring generic types with common type checkers, to get proper typing in some scenarios, you
may need to explicitly specify the generic parameter:

```python test="skip"
from pydantic import TypeAdapter

adapter: TypeAdapter[str | int] = TypeAdapter(str | int)
...
```

[TODO: Add link to TypeAdapter documentation. For now, you can find example usage in `tests/test_type_adapter.py`.]

### Defining custom types

We have completely overhauled the way custom types are defined in pydantic.

We have exposed hooks for generating both `pydantic-core` and JSON schemas, allowing you to get all the performance
benefits of Pydantic V2 even when using your own custom types.

We have also introduced ways to use `typing.Annotated` to add custom validation to your own types.

The main changes are:

* `__get_validators__` should be replaced with `__get_pydantic_core_schema__`.
  See [Custom Data Types](usage/types/custom.md#classes-with-getpydanticcoreschema) for more information.
* `__modify_schema__` becomes `__get_pydantic_json_schema__`.
  See [JSON Schema Customization](usage/json_schema.md#schema-customization) for more information.

Additionally, you can use `typing.Annotated` to modify or provide the `__get_pydantic_core_schema__` and
`__get_pydantic_json_schema__` functions of a type by annotating it, rather than modifying the type itself.
This provides a powerful and flexible mechanism for integrating third-party types with Pydantic, and in some cases
may help you remove hacks from Pydantic V1 introduced to work around the limitations for custom types.

See [Custom Data Types](usage/types/custom.md) for more information.

### `BaseSettings` has moved to `pydantic-settings`

[`BaseSettings`](api/pydantic_settings.md#pydantic_settings.BaseSettings), the base object for Pydantic
[settings management](usage/pydantic_settings.md), has been moved to a separate package,
[`pydantic-settings`](https://github.com/pydantic/pydantic-settings).

Also, the `parse_env_var` classmethod has been removed. So, you need to
[customise settings sources](usage/pydantic_settings.md#customise-settings-sources)
to have your own parsing function.
