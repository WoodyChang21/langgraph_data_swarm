YOU HAVE ACCESS TO TWO TABLES (arrivals, departures):

1. **arrivals table** — LOG OF FLIGHTS THAT ARRIVED AT KHH AIRPORT  
- EACH ROW = ONE FLIGHT THAT ARRIVED AT KHH AIRPORT
- Only includes arriving flights; has no record of whether or when the same flight departed.
- FIELDS:
    - FID (unique flight event ID)
    - FDate (flight date)
    - AirlineIATA (airline code)
    - FlightNumber (flight number)
    - DepartureAirportIATA (origin airport code - WHERE THE FLIGHT DEPARTED FROM BEFORE ARRIVING AT KHH)
    - SCHE_TYPE (schedule type, e.g. FOR_SCHE, DOM_SCHE)
    - Cancel (cancellation flag: 0 = on schedule, 1 = cancelled)
    - AircraftType (aircraft model)
    - Reg (aircraft registration code)
    - SeatCapacity, LoadCapacity (aircraft capacity)
    - Cargo (cargo weight in kilograms; 0 = no cargo, >0 = cargo weight in kg)
    - ArrivalDateTime (scheduled arrival time), amhsATA (actual arrival time)
    - RWYARR (arrival runway)
    - Bay (arrival gate/parking bay)
    - Passanger (actual passenger count)
    - logtime (record creation timestamp) 
- **DELAY = (amhsATA - ArrivalDateTime) > 900 seconds (15 minutes)**
- **INTERNATIONAL FLIGHT = `FOR_%`; DOEMSTIC FLIGHT = `DOM_%`**

2. **departures table** — LOG OF FLIGHTS THAT DEPARTED FROM KHH  
- EACH ROW = ONE DEPARTURE FLIGHT THAT DEPARTURED FROM KHH AIRPORT  
- Only includes departing flights; has no relation to any preceding arrival event of the same aircraft or airline.
- FIELDS:  
    - FID (unique flight event ID)  
    - FDate (flight date)  
    - AirlineIATA (airline code)  
    - FlightNumber (flight number)  
    - **ArrivalAirportIATA** (destination airport code - WHERE THE FLIGHT WILL ARRIVE AFTER DEPARTING FROM KHH)  
    - SCHE_TYPE (schedule type, e.g. FOR_SCHE, DOM_SCHE)
    - Cancel (cancellation flag: 0 = not cancelled, 1 = cancelled)  
    - AircraftType (aircraft model)  
    - Reg (aircraft registration number)  
    - SeatCapacity (number of seats available)  
    - LoadCapacity (maximum load capacity in kg)  
    - Cargo (cargo weight in kilograms; 0 = no cargo, >0 = cargo weight in kg)  
    - DepartureDateTime (scheduled departure time)  
    - amhsATD (actual departure time)  
    - RWYDEP (departure runway identifier)  
    - Bay (departure gate / parking bay)  
    - Passanger (actual number of passengers boarded)  
    - logtime (record creation timestamp)  
- **DELAY = (amhsATD - DepartureDateTime) > 900 seconds (15 minutes)**
- **INTERNATIONAL FLIGHT = `FOR_%`; DOEMSTIC FLIGHT = `DOM_%`**