YOU HAVE ACCESS TO TWO TABLES (arrivals, departures):

================================================
KHH Airport is ALWAYS one endpoint of every flight.
- arrivals = flights coming TO KHH FROM other airports
- departures = flights leaving FROM KHH TO other airports
================================================

1. **arrivals table** — LOG OF FLIGHTS THAT ARRIVED AT KHH AIRPORT  
- EACH ROW = ONE FLIGHT THAT ARRIVED AT KHH AIRPORT
- Only includes arriving flights; has no record of whether or when the same flight departed.
- FIELDS:
    - `FID`: Unique flight event ID
    - `FDate`: Scheduled flight date
    - `AirlineIATA`: Airline IATA code
    - `FlightNumber`: Flight number
    - `DepartureAirportIATA`: IATA code of origin airport (where the flight departed **before arriving at KHH**)
    - `SCHE_TYPE`: Schedule type (e.g., `FOR_SCHE` = International, `DOM_SCHE` = Domestic)
    - `Cancel`: Flight cancellation flag (0 = operational, 1 = cancelled)
    - `AircraftType`: Model of aircraft used
    - `Reg`: Aircraft registration code
    - `SeatCapacity`: Number of passenger seats available
    - `LoadCapacity`: Maximum cargo capacity (in kg)
    - `Cargo`: Actual cargo weight (kg); 0 if no cargo
    - `ArrivalDateTime`: Scheduled arrival time (UTC)
    - `amhsATA`: Actual arrival time (UTC)
    - `RWYARR`: Runway used for arrival
    - `Bay`: Arrival gate or parking bay
    - `Passenger`: Number of passengers onboard
    - `logtime`: Timestamp when this record was logged
- **DELAY = (amhsATA - ArrivalDateTime) > 900 seconds (15 minutes)**
- **INTERNATIONAL FLIGHT = `FOR_%`; DOEMSTIC FLIGHT = `DOM_%`**
- **DepartureAirportIATA = where the flight departed **before arriving at KHH**

2. **departures table** — LOG OF FLIGHTS THAT DEPARTED FROM KHH  
- EACH ROW = ONE DEPARTURE FLIGHT THAT DEPARTURED FROM KHH AIRPORT  
- Only includes departing flights; has no relation to any preceding arrival event of the same aircraft or airline.
- FIELDS:  
    - `FID`: Unique flight event ID
    - `FDate`: Scheduled flight date
    - `AirlineIATA`: Airline IATA code
    - `FlightNumber`: Flight number
    - `ArrivalAirportIATA`: IATA code of destination airport (where the flight is headed **after leaving KHH**)
    - `SCHE_TYPE`: Schedule type (e.g., `FOR_SCHE` = International, `DOM_SCHE` = Domestic)
    - `Cancel`: Flight cancellation flag (0 = operational, 1 = cancelled)
    - `AircraftType`: Model of aircraft used
    - `Reg`: Aircraft registration code
    - `SeatCapacity`: Number of passenger seats available
    - `LoadCapacity`: Maximum cargo capacity (kg)
    - `Cargo`: Actual cargo weight (kg); 0 if no cargo
    - `DepartureDateTime`: Scheduled departure time (UTC)
    - `amhsATD`: Actual departure time (UTC)
    - `RWYDEP`: Runway used for departure
    - `Bay`: Departure gate or parking bay
    - `Passenger`: Number of passengers onboard
    - `logtime`: Timestamp when this record was logged
- **DELAY = (amhsATD - DepartureDateTime) > 900 seconds (15 minutes)**
- **INTERNATIONAL FLIGHT = `FOR_%`; DOEMSTIC FLIGHT = `DOM_%`**
- **ArrivalAirportIATA = Where the flight is headed **after leaving KHH**