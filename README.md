# REDCap Booster

An API framework for developing external services for REDCap. Tested with Python 3.11.6.

## Installation

To run from the project folder:

```
pip install -r requirements.txt
uvicorn main:app --app-dir redcap_booster
python redcap_booster/cli.py
```

To install and run in a development environment:

```
pip install -r requirements.txt
pip install -e .
uvicorn redcap_booster.main:app
rbutils
```

## Production Deployment

In a production environment, it is recommended to use `gunicorn` as a process
manager for `uvicorn` and `systemd` to manage the `gunicorn` service.

### Gunicorn

The following command can be used to run the application with `gunicorn`:

```
gunicorn --bind=127.0.0.1:8000 -w 1 -k uvicorn.workers.UvicornWorker redcap_booster.main:app
```

You may need to adjust the `--bind` address and the number of workers (`-w`)
for your environment.

### Systemd Service

To manage the `gunicorn` process with `systemd`, you can create a service file
at `/etc/systemd/system/redcap-booster.service` with the following content.
Make sure to replace `/path/to/your/project` with the actual path to the
`redcap-booster` project directory if it differs from the example.

```ini
[Unit]
Description=Redcap Booster Gunicorn Service
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/redcap-booster
ExecStart=/home/ubuntu/.local/bin/gunicorn --bind=127.0.0.1:8000 -w 1 -k uvicorn.workers.UvicornWorker redcap_booster.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

After creating the service file, you can enable and start the service with the
following commands:

```
sudo systemctl enable redcap-booster
sudo systemctl start redcap-booster
```

### NGINX Configuration

It is recommended to use NGINX as a reverse proxy in front of the `gunicorn`
service. This allows you to handle SSL termination and other web server tasks
with NGINX.

An example NGINX configuration can be found below. You will need to customize this file for your environment, including the `server_name` and SSL certificate paths.

```
server {
    server_name redcap.ibdgc.org;

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/redcap.ibdgc.org/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/redcap.ibdgc.org/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

    location /redcap-booster/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

}

server {
    listen 80;
    server_name redcap.ibdgc.org;

    # Certbot will manage this block for renewals
    # It will temporarily add a location for /.well-known/acme-challenge/
    # and then remove it after successful renewal.
    # The 'if' block below handles the redirect for all other traffic.
    # The 'return 404;' directive was removed as it was preventing Certbot validation.

    if ($host = redcap.ibdgc.org) {
        return 301 https://$host$request_uri;
    }

}
```

**Certbot Integration:**

If you are using Certbot for SSL certificate management, ensure your NGINX
configuration includes the Certbot-managed SSL directives. Certbot will
automatically handle certificate renewals and configuration updates. The
example `nginx_reverse_proxy.conf` includes directives like
`ssl_certificate /etc/letsencrypt/live/redcap.ibdgc.org/fullchain.pem;` and
`include /etc/letsencrypt/options-ssl-nginx.conf;` which are common for
Certbot integration.

See <https://www.uvicorn.org/deployment/> for more information on deployment
options.

## External Configuration

The deployment of this application involves several components outside of this
codebase.

### EC2 Instance Setup

The application is designed to be run on a Linux-based server, such as an
Amazon EC2 instance. The server should have Python, `pip`, and `nginx`
installed.

The security group for the EC2 instance should be configured to allow incoming
traffic on port 80 (for HTTP) and port 443 (for HTTPS).

### DNS Configuration

To make the application accessible via a domain name, you will need to
configure the DNS records for your domain. An `A` record should be created to
point your domain (e.g., `redcap.ibdgc.org`) to the public IP address of your
EC2 instance.

### REDCap Webhook Setup

To integrate the `redcap-booster` application with REDCap, you need to
configure a "Data Entry Trigger" in your REDCap project.

1.  In your REDCap project, go to the "Project Setup" page.
2.  Click on the "Additional customizations" button.
3.  Check the "Data Entry Trigger" box.
4.  Enter the URL where the `redcap-booster` API is available. This URL should
    include the API key for your project. For example:

    ```
    https://redcap.ibdgc.org/redcap-booster/?key=<api_key>
    ```

    Replace `<api_key>` with the API key you generated for your project.

This will cause REDCap to send a `POST` request to your `redcap-booster`
application every time a data entry form is saved.

## Configuration

To enable use with a specific REDCap project, the project ID must be listed in
your `.env` file, e.g.:

```
root_path = "/redcap-booster"

# 12345 IBDGC Participant Registration (MSSM REDCap)
pids = ["12345"]

id_gen = '{"db":"id_gen.db"}'
id_gen_12345 = '{"form_triggers":["registration_form"], "id_field":"consortium_id"}'
```

Multiple project IDs can be listed, separated by commas. In addition, you need
to add to your `.secrets` folder a file named `token_11659` containing a
valid REDCap API token and a file named `key_11659` containing a
project-specific API key that can be generated in Python with:

```python
import secrets
secrets.token_urlsafe(24)
```

## Built-In Services

### ID Assignment

A service called `id_gen` is available for assigning unique IDs. To configure
this service, add the following to your `.env` file:

```
id_gen = '{"db":"<database_file>"}'
id_gen_11659 = '{"form_triggers":["<form_name>"], "id_field":"<field_name>"}'
```

and add a list of IDs to the database with:

```
rbutils id-gen load-ids <filename>
```

This service can be easily reused and customized. For example, suppose you
want to inject a second piece of information into a REDCap project for which
you are already using `id_gen`. To do this, create a new file named
`myservice.py` containing the following:

```python
from redcap_booster.services import id_gen
from redcap_booster.services.id_gen.db import DatabaseAccess
from functools import partial

service = 'my_service'
db = DatabaseAccess(service)

cli = id_gen.generate_cli(db, id_gen.commands)
run = partial(id_gen.run, service=service, db=db)
```

and place this in a directory listed in the `plugin_dirs` setting. You may
then configure the new service as described above, and load the items to be
injected into the database via the `rbutils` command. If necessary, you may
even replace the entire `run()` function.

## Database ID Correction Process

In some cases, it may be necessary to manually correct the IDs in the `id_gen`
database. This is a complex process that requires a two-phase update to avoid
violating the `UNIQUE` constraint on the `id` column in the database and the
corresponding unique field in REDCap.

The following scripts are provided to facilitate this process:

- `generate_intermediate_ids.py`: Generates a CSV file with temporary,
  unique "nonsense" IDs.
- `update_records_v6.py`: Performs a two-phase transactional update of the
  IDs in the database.

Here is the step-by-step process for correcting the IDs:

1.  **Create a `corrections.csv` file.** This file should have two columns:
    `current_id` and `corrected_id`. Each row should contain an ID that needs
    to be corrected and the ID that it should be corrected to.

2.  **Generate an intermediate corrections file.** Run the
    `generate_intermediate_ids.py` script to create a new CSV file with a
    third column, `intermediate_id`. This script will generate a unique,
    random ID for each correction.

    ```bash
    python generate_intermediate_ids.py corrections.csv corrections_intermediate.csv
    ```

3.  **Perform the Phase 1 update (to intermediate IDs).**
    a. Create a `corrections_phase1.csv` file with the `current_id` from
    `corrections_intermediate.csv` and the `intermediate_id` as the
    `corrected_id`.
    b. Run the `update_records_v6.py` script with this file:

        ```bash
        python update_records_v6.py id_gen_original.db corrections_phase1.csv <project_id>
        ```

    c. Trigger the `redcap-booster` webhook for all affected records. This
    will update the records in REDCap to have the temporary, intermediate
    IDs.

4.  **Perform the Phase 2 update (to final IDs).**
    a. Create a `corrections_phase2.csv` file with the `intermediate_id`
    from `corrections_intermediate.csv` as the `current_id` and the
    original `corrected_id` as the new `corrected_id`.
    b. Run the `update_records_v6.py` script with this file:

        ```bash
        python update_records_v6.py id_gen_original.db corrections_phase2.csv <project_id>
        ```

    c. Trigger the `redcap-booster` webhook for all affected records again.
    This will update the records in REDCap to have the final, correct IDs.

This two-phase process ensures that there are no `UNIQUE` constraint
violations in either the `id_gen` database or REDCap during the update
process.
