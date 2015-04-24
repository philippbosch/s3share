# s3share

_s3share_ is a simple command line tool to share any file with somebody via [Amazon S3](https://aws.amazon.com/s3/). It will upload the file itself, create a simple HTML page with a download link and output the URL to it.

![Demo](https://s3.amazonaws.com/f.cl.ly/items/3Y403n2y0e2v2q2F223R/Screen%20Recording%202015-04-24%20at%2011.02%20vorm..gif)


## Installation

Using [pip](https://pip.pypa.io/):

```shell
$ pip install s3share
```

From source:

```shell
$ git clone https://github.com/philippbosch/s3share.git
$ cd s3share
$ python setup.py install
```

## Configuration

Create a file called `.s3share` with the following content:

```ini
[S3]
bucket_name = …
aws_access_key_id = …
aws_secret_access_key = …
```

`bucket_name` should be set to the name of an S3 bucket that you need to create manually, e.g. through the [AWS Console](https://console.aws.amazon.com/s3/home).

`aws_access_key_id` and `aws_secret_access_key` should be set to the respective AWS credentials. See [here](http://docs.aws.amazon.com/general/latest/gr/getting-aws-sec-creds.html) to find out how to create or retrieve these. You can also omit these two options if you have `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` set up as environment variables.


## Usage

#### TL;DR:

```shell
$ s3share /path/to/some/file
```

#### Available arguments
```shell
$ s3share -h
usage: s3share [-h] [--no-progress] [--overwrite] file

positional arguments:
  file           the path to the file to be uploaded

optional arguments:
  -h, --help     show this help message and exit
  --no-progress  do not show a progress bar
  --overwrite    overwrite existing files
```

## Nice URLs – custom domains

Given your `bucket_name` configuration option is set to `"foo-bar"`, the resulting URL will be `http://foo-bar.s3.amazonaws.com/random-string`.

You can also use a custom domain like `transfer.mydomain.com`. For this you first need to set up a DNS record for the desired hostname with your DNS provider and make it a `CNAME` record pointing to `s3.amazonaws.com`. Then create a bucket with the same name as the hostname (`transfer.mydomain.com` in this example). The resulting URLs will then be `http://transfer.mydomain.com/random-string`.

## License

[MIT](http://philippbosch.mit-license.org/)
