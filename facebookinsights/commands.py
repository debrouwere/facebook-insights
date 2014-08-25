# encoding: utf-8

import click

@click.group()
@click.option('--client-id', 
    help='the app id to your facebook app', 
    envvar='FACEBOOK_INSIGHTS_CLIENT_ID')
@click.option('--client-secret', 
    help='the client secret to your facebook app', 
    envvar='FACEBOOK_INSIGHTS_CLIENT_SECRET')
@click.argument('page') # help='the name of the Facebook Page you would like to fetch insights from'
def cli(page=None):
    # TODO: if no page is specified, list all pages that we've saved
    pass

@cli.command()
@click.option('--force', help='ignore any existing credentials')
def authorize():
    pass

@cli.command()
def ls():
    pass

@cli.command()
@cli.option('-s', '--since')
@cli.option('-u', '--until')
@cli.option('-m', '--months', default=0)
@cli.option('-d', '--days', default=0)
@cli.option('-p', '--period')
@cli.option('-M', '--metrics')
def page():
    pass

@cli.command()
@cli.option('--since')
@cli.option('--until')
@cli.option('--months', default=0)
@cli.option('--days', default=0)
@cli.option('--metrics')
def posts():
    # a period doesn't make sense for posts, as all post metrics 
    # are lifetime metrics
    pass

"""
insights posts Guardian\ US --metrics page_impressions --since 2014-05-01 --days 5
"""