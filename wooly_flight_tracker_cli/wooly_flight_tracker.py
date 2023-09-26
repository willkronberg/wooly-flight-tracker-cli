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
@click.argument("name")
def greet(name: str):
    logging.info(f"Hello, {name}!")


cli.add_command(greet)


@click.command()
@click.argument("call_sign")
def get_flight_details(call_sign: str):
    tracker = FlightTrackerService()
    flight_details = tracker.get_flight_details(call_sign)
    logging.info(flight_details.model_dump())


cli.add_command(get_flight_details)


@click.command()
@click.argument("airline_name")
@click.argument("flight_number")
def get_flight_status(airline_name: str, flight_number: str):
    tracker = FlightTrackerService()
    flight_status = tracker.get_flight_status(airline_name, flight_number)
    logging.info(flight_status.model_dump())


cli.add_command(get_flight_status)


@click.command()
@click.argument("airline_name")
@click.argument("flight_number")
def track_flight(airline_name: str, flight_number: str):
    tracker = FlightTrackerService()
    tracker.track_flight(airline_name, flight_number)


cli.add_command(track_flight)


@click.command()
@click.argument("airline")
def get_all_flights(airline: str):
    tracker = FlightTrackerService()
    tracker.get_all_flights(airline)


cli.add_command(get_all_flights)


@click.command()
@click.argument("airline_name")
def get_airline_info(airline_name: str):
    tracker = FlightTrackerService()
    airline = tracker.get_airline_information(airline_name)
    print(airline)


cli.add_command(get_airline_info)


def main():
    cli(prog_name="cli")


if __name__ == "__main__":
    main()
