"""
optimizer.py

Solves for the cheapest flight(s) based on filtered data and constraints.
Uses Linear Programming via PuLP.
"""

import pandas as pd
from pulp import LpProblem, LpVariable, lpSum, LpMinimize, LpBinary, PULP_CBC_CMD

def find_cheapest_itinerary(df, max_duration=None, preferred_departure=None, latest_arrival=None):
    """
    Solves an LP model to find the cheapest flight(s) based on input data.

    Parameters:
    - df (DataFrame): Filtered DataFrame containing flight options.

    Returns:
    - DataFrame: Selected flight(s) from the input, marked as optimal.
    - float: Total price of the optimal itinerary.
    """
    # Apply constraint filters to reduce the LP size
    if max_duration is not None:
        df = df[df['duration'] <= max_duration]

    if preferred_departure is not None:
        df = df[df['departure_time'] == preferred_departure]

    if latest_arrival is not None:
        df = df[df['arrival_time'] == latest_arrival]

    if df.empty:
        print("⚠️ No flights available that match the given constraints.")
        return pd.DataFrame(), 0
    
    # Create the LP problem
    prob = LpProblem("FlightFareMinimization", LpMinimize)

    # Create binary decision variables for each flight
    flight_vars = {
        i: LpVariable(f"flight_{i}", cat=LpBinary)
        for i in df.index
    }

    # Objective: Minimize total price
    prob += lpSum(flight_vars[i] * df.loc[i, "price"] for i in df.index)

    # Constraint: Select exactly one flight for now (simple version)
    prob += lpSum(flight_vars[i] for i in df.index) == 1, "SelectOneFlight"

    # Solve
    prob.solve(PULP_CBC_CMD(msg=False))

    # Extract selected flight(s)
    selected_indices = [i for i in df.index if flight_vars[i].value() == 1.0]
    selected_flights = df.loc[selected_indices].copy()
    total_price = selected_flights["price"].sum()

    return selected_flights.reset_index(drop=True), total_price

def find_multi_leg_itinerary(df, source, destination):
    """
    Finds the cheapest itinerary from source to destination using one or more flights.
    Uses a flow model to connect flights across cities.
    """

    from pulp import LpProblem, LpVariable, lpSum, LpMinimize, LpBinary, PULP_CBC_CMD

    df = df.copy()
    df.reset_index(drop=True, inplace=True)

    # Create a variable for each flight
    flight_vars = {
        i: LpVariable(f"flight_{i}", cat=LpBinary)
        for i in df.index
    }

    prob = LpProblem("MultiLegFlightOptimizer", LpMinimize)

    # Objective: Minimize total price
    prob += lpSum(flight_vars[i] * df.loc[i, "price"] for i in df.index)

    # 🔄 Build city flow constraints
    all_cities = set(df["source_city"]).union(set(df["destination_city"]))

    for city in all_cities:
        in_flights = [i for i in df.index if df.loc[i, "destination_city"] == city]
        out_flights = [i for i in df.index if df.loc[i, "source_city"] == city]

        if city == source:
            # Must depart from source once
            prob += lpSum(flight_vars[i] for i in out_flights) == 1
            prob += lpSum(flight_vars[i] for i in in_flights) == 0

        elif city == destination:
            # Must arrive at destination once
            prob += lpSum(flight_vars[i] for i in in_flights) == 1
            prob += lpSum(flight_vars[i] for i in out_flights) == 0

        else:
            # Intermediate cities: flow conservation
            prob += lpSum(flight_vars[i] for i in in_flights) == \
                    lpSum(flight_vars[i] for i in out_flights)

    # Solve the LP
    prob.solve(PULP_CBC_CMD(msg=False))

    selected_indices = [i for i in df.index if flight_vars[i].value() == 1.0]
    selected_flights = df.loc[selected_indices].copy()
    total_price = selected_flights["price"].sum()

    return selected_flights.sort_values("departure_time").reset_index(drop=True), total_price