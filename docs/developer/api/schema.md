# OpenApi schema

The frontend need up to date schemas ! If you change the api you need to upgrade the schema by running : `docker compose run --rm api funkwhale-manage spectacular > ./api/funkwhale_api/common/schema.yml`.

Then you need to upgrade the frontend schema has well by running `yarn generate-types-from-local-schema`.

Be aware that `get_signup_form_additional_fields_serializer` can tweak the schema generation.
