import argparse
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import os.path
import random
import string
import sys

import boto
from boto.s3.connection import SubdomainCallingFormat, VHostCallingFormat


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='the path to the file to be uploaded')
    parser.add_argument('--no-progress', help='do not show a progress bar', action='store_true')
    parser.add_argument('--overwrite', help='overwrite existing files', action='store_true')
    args = parser.parse_args()

    # Check for configuration file
    config_file = os.path.expanduser('~/.s3share')
    if not os.path.isfile(config_file):
        sys.stderr.write('Config file does not exist. Please create {0} and put something like this in there:\n\n[S3]\nbucket_name = name-of-the-target-bucket\n'.format(config_file))
        return 1

    # Read configuration file
    config = configparser.ConfigParser()
    config.read([config_file])

    # Read bucket name from config
    if not config.has_section('S3') or not config.has_option('S3', 'bucket_name'):
        sys.stderr.write('Config file is missing "bucket_name" option in "[S3]" section.\n')
        return 2
    bucket_name = config.get('S3', 'bucket_name')

    # Check if the file to be uploaded actually exists
    if not os.path.isfile(args.file):
        sys.stderr.write('File does not exists: {0}\n'.format(args.file))
        return 3

    # Determine calling format to use
    calling_format = SubdomainCallingFormat()

    if '.' in bucket_name:
        calling_format = VHostCallingFormat()

        # Monkey-patch SSL to skip hostname verification
        import ssl
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context

    conn_kwargs = {'calling_format': calling_format}

    # Set AWS keys
    if config.has_option('S3', 'aws_access_key_id'):
        conn_kwargs['aws_access_key_id'] = config.get('S3', 'aws_access_key_id')
    if config.has_option('S3', 'aws_secret_access_key'):
        conn_kwargs['aws_secret_access_key'] = config.get('S3', 'aws_secret_access_key')

    # Connect to S3
    conn = boto.connect_s3(**conn_kwargs)

    # Get the bucket
    try:
        bucket = conn.get_bucket(bucket_name)
    except boto.exception.S3ResponseError as e:
        if e.status == 404:
            sys.stderr.write('Bucket does not exist: {0}\n'.format(bucket_name))
        elif e.status == 403:
            sys.stderr.write('Missing or invalid AWS credentials.\n')
        else:
            sys.stderr.write('Error while connecting to S3. {0} {1}\n'.format(e.status, e.message))
        return 4

    # Callback for progress display
    def progress(current, total):
        if not args.no_progress:
            progress = float(current) / total
            length = 50
            sys.stdout.write('\r[{0}>{1}] {2:3d}% ({3}/{4} kB)'.format(
                '-' * int(round(length * progress)),
                ' ' * int(round(length * (1 - progress))),
                int(round(progress * 100)),
                current / 1024,
                total / 1024
            ))

    # Create a new key
    key_id = os.path.basename(args.file)
    if not args.overwrite and bucket.get_key(key_id) is not None:
        sys.stderr.write('File "{0}" already exists. Use --overwrite if you want to upload anyway.\n'.format(key_id))
        return 5

    key = bucket.new_key(key_id)

    # Upload the file
    key.set_contents_from_filename(args.file, policy='public-read', cb=progress, num_cb=1000)

    # Generate the public URL for the uploaded file
    url = key.generate_url(0, query_auth=False, force_http=True)

    # Template for the download page
    template = '''
    <!doctype html>
    <html>
        <head>
            <meta charset="utf-8">
            <title>Download</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.4/css/bootstrap.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootswatch/3.3.4/yeti/bootstrap.min.css">
            <style>
                body {{
                    display: table-cell;
                    vertical-align: middle;
                    width: 100vw;
                    height: 100vh;
                }}

                h2 {{
                    margin-bottom: 32px;
                }}
            </style>
        </head>
        <body>
            <div class="container center-block">
                <div class="text-center">
                    <h2>{name}</h2>
                    <p>
                        <a class="btn btn-primary btn-lg" href="{url}" role="button" download>
                            <span class="glyphicon glyphicon-download-alt"></span>
                            Download
                        </a>
                        &nbsp;&nbsp;
                        <span class="text-muted">{size} MB</span>
                    </p>
                </div>
            </div>
        </body>
    </html>
    '''

    # Render the template
    html = template.format(name=key.name, size=round(key.size / 1024 / 102.4) / 10.0, type=key.content_type, url=url)

    # Upload the download page
    id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    html_key = bucket.new_key(id)
    html_key.content_type = 'text/html; charset=utf-8'
    html_key.set_contents_from_string(html, policy='public-read')

    # Generate and output the public URL for the download page
    html_url = html_key.generate_url(0, query_auth=False, force_http=True)
    if not args.no_progress:
        sys.stdout.write('\n')
    sys.stdout.write('{0}\n'.format(html_url))


if __name__ == '__main__':
    sys.exit(main())
