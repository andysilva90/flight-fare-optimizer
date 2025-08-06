"""
data_prep.py

Flight data filtering module.
Provides utility functions to filter flights based on user-defined criteria.

Author: Andres
"""

import pandas as pd

def filter_flights(df,
                   source=None,
                   destination=None,
                   max_stops=None,
                   seat_class=None,
                   preferred_departure=None,
                   max_duration=None,
                   max_price=None,
                   direct_only=True):
    
    """
    Filter the flight dataset based on user preferences.

    Parameters:
    - df (DataFrame): The full dataset.
    - source (str): Source city name.
    - destination (str): Destination city name.
    - max_stops (int): Max number of stops allowed (0, 1, 2).
    - seat_class (str): "Economy" or "Business".
    - preferred_departure (str): Departure time label (e.g. "Morning", "Evening").
    - max_duration (float): Maximum allowed duration in hours.
    - max_price (float): Optional price cap.
    - direct_only(boolean): Define if it is a direct fly or not (default to 'True').

    Returns:
    - DataFrame: Filtered subset of flights.
    """

    filtered = df.copy()

    if direct_only:
        if source is not None:
            filtered = filtered[filtered['source_city'] == source]

        if destination is not None:
            filtered = filtered[filtered['destination_city'] == destination]

    if seat_class is not None:
        filtered = filtered[filtered["class"] == seat_class]

    if max_stops is not None:
        stop_mapping = {
            'zero': 0,
            'one': 1,
            'two_or_more': 2
            }
        filtered = filtered[filtered['stops'].map(lambda x: stop_mapping.get(x.lower(), 2)) <= max_stops]

    if preferred_departure is not None:
        filtered = filtered[filtered['departure_time'] == preferred_departure]

    if max_duration is not None:
        filtered = filtered[filtered['duration'] <= max_duration]

    if max_price is not None:
        filtered = filtered[filtered['price'] <= max_price]

    return filtered.reset_index(drop=True)