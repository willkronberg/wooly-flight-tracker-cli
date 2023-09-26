import logging
from time import sleep
from datetime import datetime

from tqdm import tqdm
from FlightRadar24 import Flight, FlightRadar24API
from retry import retry

from wooly_flight_tracker_cli.exceptions.flight_not_found import FlightNotFoundException
from wooly_flight_tracker_cli.models.flights import FlightDetails, FlightStatus, Airline

logger = logging.Logger(__name__)


class FlightTrackerService:
    client: FlightRadar24API

    def __init__(self):
        self.client = FlightRadar24API()

    def get_airline_information(self, airline_name: str) -> Airline:
        airlines = self.client.get_airlines()

        found_airlines = []
        for item in airlines:
            if item["Name"] == airline_name:
                found_airlines.append(Airline(**item))

        if len(found_airlines) == 0:
            raise Exception("Could not find the requested airline")
        elif len(found_airlines) > 1:
            raise Exception("Found too many airlines with that name")
        else:
            return found_airlines[0]

    def get_flight_status(self, airline_name: str, flight_number: str) -> FlightStatus:
        airline = self.get_airline_information(airline_name=airline_name)
        call_sign = f"{airline.icao}{flight_number}"
        flight = self.__find_flight__(call_sign)
        flight_details = self.__retrieve_flight_details__(flight)

        return FlightStatus(
            call_sign=flight_details.identification.callsign,
            is_live=flight_details.status.live,
            origin_airport_name=flight_details.airport.origin.name,
            origin_coordinates=(
                flight_details.airport.origin.position.latitude,
                flight_details.airport.origin.position.longitude,
            ),
            destination_airport_name=flight_details.airport.destination.name,
            destination_coordinates=(
                flight_details.airport.destination.position.latitude,
                flight_details.airport.destination.position.longitude,
            ),
            current_coordinates=(
                flight_details.trail[0].lat,
                flight_details.trail[0].lng,
            ),
            current_coordinates_last_update=datetime.fromtimestamp(
                flight_details.trail[0].ts
            ),
            scheduled_departure=datetime.fromtimestamp(
                flight_details.time.scheduled.departure
            ),
            scheduled_arrival=datetime.fromtimestamp(
                flight_details.time.scheduled.arrival
            ),
            estimated_arrival=datetime.fromtimestamp(
                flight_details.time.estimated.arrival
            )
            if flight_details.time.estimated.arrival
            else None,
            actual_departure=datetime.fromtimestamp(flight_details.time.real.departure)
            if flight_details.time.real.departure
            else None,
            actual_arrival=datetime.fromtimestamp(flight_details.time.real.arrival)
            if flight_details.time.real.arrival
            else None,
        )

    def track_flight(self, airline_name: str, flight_number: str, poll_seconds: int):
        flight_status = self.get_flight_status(airline_name, flight_number)

        print(
            f"Tracking Flight {flight_status.call_sign} - {flight_status.origin_airport_name} to {flight_status.destination_airport_name}"
        )
        progress_bar = tqdm(
            total=flight_status.total_distance,
            desc="Flight Progress",
            leave=False,
            bar_format="{l_bar}|{bar}| {n:.2f}/{total:.2f} {unit}{postfix}",
            unit="miles",
        )

        last_distance_traveled = flight_status.traveled_distance
        progress_bar.update(flight_status.traveled_distance)

        while flight_status.status != "ARRIVED":
            flight_status = self.get_flight_status(airline_name, flight_number)

            if flight_status.status == "WAITING_TO_DEPART":
                progress_bar.set_postfix_str("Waiting to Depart")
            elif flight_status.status == "IN_FLIGHT":
                progress_bar.set_postfix_str(
                    f"Time Remaining: {str(flight_status.remaining_time)}"
                )

                if flight_status.traveled_distance != last_distance_traveled:
                    progress_bar.update(
                        flight_status.traveled_distance - last_distance_traveled
                    )
                    last_distance_traveled = flight_status.traveled_distance

            sleep(poll_seconds)

        progress_bar.close()

        print(
            f"The flight arrived to it's destination at {flight_status.actual_arrival}"
        )

    def get_flight_details(self, call_sign: str) -> FlightDetails:
        flight = self.__find_flight__(call_sign)
        return self.__retrieve_flight_details__(flight)

    def get_all_flights(self, airline: str):
        all_flights = self.client.get_flights(airline=airline)

        for index, item in enumerate(all_flights):
            print(f"Starting Flight {index + 1} of {len(all_flights)}")
            self.__retrieve_flight_details__(item)

    def __find_flight__(self, call_sign: str) -> Flight:
        airline_icao = call_sign[:3]
        all_flights = self.client.get_flights(airline=airline_icao)

        for item in all_flights:
            if item.callsign == call_sign:
                return item

        raise FlightNotFoundException(call_sign)

    @retry(exceptions=Exception, tries=10, backoff=2)
    def __retrieve_flight_details__(self, flight: Flight) -> FlightDetails:
        response = self.client.get_flight_details(flight)
        return FlightDetails.model_validate(response)
