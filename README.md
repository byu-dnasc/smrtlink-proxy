# Installation

### Download

The smrtlink-repository must be cloned to your user's home directory

### Setup

The container image must be built by the same user who will run it. So, execute
the following commands as the user who will end up running it:

1. Load bash functions into your shell with `. manage.sh`
2. run `build`
3. run `start`

### NGINX configuration templates

The NGINX configuration files essentially make up smrtlink-proxy.
These files begin as templates containing references to variables.
These variable references must be replaced with the variable's value.

This substitution can occur when the container image is built, but
during template development, it is more convenient to use the `test_template`
function to make config files from the templates. This command also
feeds the generated config to NGINX for validation.

### Troubleshooting

Serveral bash functions exist in `manage.sh` for troubleshooting smrtlink-proxy's
level of functionality. These include `web`, `http`, `https`.