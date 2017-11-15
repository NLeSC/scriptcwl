import click
import json


@click.command()
@click.argument('x', type=int)
@click.argument('y', type=int)
def add(x, y):
    click.echo(json.dumps({'answer': x+y}))


if __name__ == '__main__':
    add()
