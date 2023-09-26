from datetime import datetime, timedelta
from typing import Any, List, Optional, Tuple

from geopy.distance import geodesic
from pydantic import BaseModel, computed_field, Field


class FlightDetailsIdentificationNumber(BaseModel):
    default: Optional[str]
    alternative: Optional[str]


class FlightDetailsIdentification(BaseModel):
    id: str
    row: int
    number: FlightDetailsIdentificationNumber
    callsign: Optional[str]


class FlightDetailsStatusGenericStatus(BaseModel):
    text: str
    color: str
    type: str


class FlightDetailsStatusGeneric(BaseModel):
    status: FlightDetailsStatusGenericStatus


class FlightDetailsStatus(BaseModel):
    live: bool
    text: str
    icon: Optional[str]
    estimated: Optional[str]
    ambiguous: bool
    generic: FlightDetailsStatusGeneric


class FlightDetailsAircraftModel(BaseModel):
    code: str
    text: str


class FlightDetailsAircraftImageItem(BaseModel):
    src: str
    link: str
    copyright: str
    source: str


class FlightDetailsAircraftImages(BaseModel):
    thumbnails: List[FlightDetailsAircraftImageItem]
    medium: List[FlightDetailsAircraftImageItem]
    large: List[FlightDetailsAircraftImageItem]


class FlightDetailsAircraft(BaseModel):
    model: FlightDetailsAircraftModel
    countryId: int
    registration: str
    age: Optional[int]
    msn: Optional[Any]
    images: FlightDetailsAircraftImages
    hex: str


class FlightDetailsAirlineCode(BaseModel):
    iata: str
    icao: str


class FlightDetailsAirline(BaseModel):
    name: str
    short: str
    code: FlightDetailsAirlineCode
    url: str


class FlightDetailsAirportItemCode(BaseModel):
    iata: str
    icao: str


class FlightDetailsAirportItemPositionCountry(BaseModel):
    id: Optional[int]
    name: str
    code: str


class FlightDetailsAirportItemPositionRegion(BaseModel):
    city: str


class FlightDetailsAirportItemPosition(BaseModel):
    latitude: float
    longitude: float
    altitude: int
    country: FlightDetailsAirportItemPositionCountry
    region: FlightDetailsAirportItemPositionRegion


class FlightDetailsAirportItemTimezone(BaseModel):
    name: str
    offset: int
    offsetHours: str
    abbr: str
    abbrName: str
    isDst: bool


class FlightDetailsAirportItemInfo(BaseModel):
    terminal: Optional[str]
    baggage: Optional[str]
    gate: Optional[str]


class FlightDetailsAirportItem(BaseModel):
    name: str
    code: FlightDetailsAirportItemCode
    position: FlightDetailsAirportItemPosition
    timezone: FlightDetailsAirportItemTimezone
    visible: bool
    website: Optional[str]
    info: FlightDetailsAirportItemInfo


class FlightDetailsAirport(BaseModel):
    origin: FlightDetailsAirportItem
    destination: Optional[FlightDetailsAirportItem]
    real: Optional[FlightDetailsAirportItem]


class FlightDetailsTimeOther(BaseModel):
    eta: Optional[int]
    updated: Optional[int]


class FlightDetailsTimeHistorical(BaseModel):
    flighttime: str
    delay: str


class FlightDetailsTimeItem(BaseModel):
    departure: Optional[int]
    arrival: Optional[int]


class FlightDetailsTime(BaseModel):
    scheduled: FlightDetailsTimeItem
    real: FlightDetailsTimeItem
    estimated: FlightDetailsTimeItem
    other: FlightDetailsTimeOther
    historical: Optional[FlightDetailsTimeHistorical]


class FlightDetailsTrailPoint(BaseModel):
    lat: float
    lng: float
    alt: int
    spd: int
    ts: int
    hd: int


class FlightDetails(BaseModel):
    identification: FlightDetailsIdentification
    status: FlightDetailsStatus
    level: str
    promote: bool
    aircraft: FlightDetailsAircraft
    airline: FlightDetailsAirline
    owner: Optional[Any]
    airspace: Optional[Any]
    airport: FlightDetailsAirport
    time: FlightDetailsTime
    trail: List[FlightDetailsTrailPoint]


class FlightStatus(BaseModel):
    call_sign: str
    is_live: bool
    origin_airport_name: str
    origin_coordinates: Tuple[float, float]
    destination_airport_name: str
    destination_coordinates: Tuple[float, float]
    current_coordinates: Tuple[float, float]
    current_coordinates_last_update: datetime
    scheduled_departure: datetime
    scheduled_arrival: datetime
    estimated_arrival: Optional[datetime]
    actual_departure: Optional[datetime]
    actual_arrival: Optional[datetime]

    @computed_field
    @property
    def total_distance(self) -> float:
        return geodesic(self.origin_coordinates, self.destination_coordinates).miles

    @computed_field
    @property
    def remaining_distance(self) -> float:
        return geodesic(self.current_coordinates, self.destination_coordinates).miles

    @computed_field
    @property
    def traveled_distance(self) -> float:
        return self.total_distance - self.remaining_distance

    @computed_field
    @property
    def completed_distance_percent(self) -> float:
        return (
            (self.total_distance - self.remaining_distance) / self.total_distance
        ) * 100

    @computed_field
    @property
    def total_time(self) -> timedelta:
        return self.scheduled_arrival - self.scheduled_departure

    @computed_field
    @property
    def remaining_time(self) -> timedelta:
        return self.estimated_arrival - datetime.now()

    @computed_field
    @property
    def status(self) -> str:
        if self.actual_departure is None:
            return "WAITING_TO_DEPART"
        elif self.actual_arrival is not None:
            return "ARRIVED"
        else:
            return "IN_FLIGHT"


class Airline(BaseModel):
    name: str = Field(alias="Name")
    code: str = Field(alias="Code")
    icao: str = Field(alias="ICAO")
