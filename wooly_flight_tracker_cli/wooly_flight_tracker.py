import logging

import click

from wooly_flight_tracker_cli.services.flight_tracker_service import (
    FlightTrackerService,
)

logging.basicConfig(level=logging.INFO)


@click.group("cli")
@click.pass_context
def cli(ctx):
    pass


@click.command()
@click.argument("airline_name")
@click.argument("flight_number")
def get_flight_status(airline_name: str, flight_number: str):
    tracker = FlightTrackerService()
    flight_status = tracker.get_flight_status(airline_name, flight_number)
    print(flight_status.model_dump_json(indent=2))


cli.add_command(get_flight_status)


@click.command()
@click.argument("airline_name")
@click.argument("flight_number")
@click.option("-p", "--poll-seconds", "poll_seconds", default=30, show_default=True)
def track_flight(airline_name: str, flight_number: str, poll_seconds: int):
    tracker = FlightTrackerService()
    tracker.track_flight(airline_name, flight_number, poll_seconds)


cli.add_command(track_flight)


def main():
    cli(prog_name="cli")


if __name__ == "__main__":
    main()
