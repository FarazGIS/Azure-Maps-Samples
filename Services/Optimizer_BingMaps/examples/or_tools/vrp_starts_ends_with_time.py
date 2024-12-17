#!/usr/bin/env python3
# Copyright 2010-2022 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START program]
"""Simple Vehicles Routing Problem."""

# [START import]
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math
# [END import]


# [START data_model]
def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data["distance_matrix"] = [
        # fmt: off
      [0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354, 468, 776, 662],
      [548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674, 1016, 868, 1210],
      [776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164, 1130, 788, 1552, 754],
      [696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822, 1164, 560, 1358],
      [582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708, 1050, 674, 1244],
      [274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628, 514, 1050, 708],
      [502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856, 514, 1278, 480],
      [194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320, 662, 742, 856],
      [308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662, 320, 1084, 514],
      [194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388, 274, 810, 468],
      [536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764, 730, 388, 1152, 354],
      [502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114, 308, 650, 274, 844],
      [388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194, 536, 388, 730],
      [354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0, 342, 422, 536],
      [468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536, 342, 0, 764, 194],
      [776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274, 388, 422, 764, 0, 798],
      [662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730, 536, 194, 798, 0],
        # fmt: on
    ]
    data["num_vehicles"] = 4
    data["depot"] = 0
    data["vehicle_shifts"] = [
        (540, 1080),
        (540, 1080),
        (540, 1080),
        (540, 1080)
    ]
    return data
    # [END data_model]


# [START solution_printer]
def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f"Objective: {solution.ObjectiveValue()}")

    # Display dropped nodes.
    dropped_nodes = 'Dropped nodes:'
    for index in range(routing.Size()):
        if routing.IsStart(index) or routing.IsEnd(index):
            continue
        if solution.Value(routing.NextVar(index)) == index:
            node = manager.IndexToNode(index)
            dropped_nodes += f' {node}'
    dropped_nodes += '\n\n'
    print(dropped_nodes)

    # Display routes
    max_route_distance = 0
    for vehicle_id in range(manager.GetNumberOfVehicles()):
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        index = routing.Start(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            time_var = routing.GetDimensionOrDie('Time').CumulVar(index)
            plan_output += f'Node {node_index}: Time: {solution.Value(time_var)}\n'
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
        node_index = manager.IndexToNode(index)
        time_var = routing.GetDimensionOrDie('Time').CumulVar(index)
        plan_output += f'Node {node_index}: Time: {solution.Value(time_var)}\n'
        plan_output += f"Distance of the route: {route_distance}m\n"
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    print(f"Maximum of the route distances: {max_route_distance}m")
    # [END solution_printer]


def main():
    """Entry point of the program."""
    # Instantiate the data problem.
    # [START data]
    data = create_data_model()
    # [END data]

    # Create the routing index manager.
    # [START index_manager]
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    )
    # [END index_manager]

    # Create Routing Model.
    # [START routing_model]
    routing = pywrapcp.RoutingModel(manager)
    # [END routing_model]

    # Create and register a transit callback.
    # [START transit_callback]
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    # [END transit_callback]

    # Define cost of each arc.
    # [START arc_cost]
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    # [END arc_cost]

    # Add Distance constraint.
    # [START distance_constraint]
    dimension_name = "Distance"
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        2000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        'Distance',
    )
    distance_dimension = routing.GetDimensionOrDie('Distance')
    distance_dimension.SetGlobalSpanCostCoefficient(100)
    # [END distance_constraint]

    # Add Time constraint.
    # [START time_constraint]
    def time_callback(from_index, to_index):
        service_time = 10
        vehicle_speed_kph = 50

        # Calculate travel time based on distance and speed
        # Note: the sample matrix is in meters and the routes are too short for an 8 hour shift
        # but if i use it as kilometers, routes are too long for the shift
        # so i will divide to a random number like 5 to have a nice looking time duration in this sample
        distance_km = distance_callback(from_index, to_index) / 5
        travel_time_min = (distance_km / vehicle_speed_kph) * 60
        total_time = math.ceil(travel_time_min + service_time)

        return total_time
        # return 10

    time_callback_index = routing.RegisterTransitCallback(time_callback)

    routing.AddDimension(
        time_callback_index,
        0,  # Maximum waiting time vehicle
        20000,  # Maximum time per vehicles
        False,  # Slack (allow waiting time)
        'Time'
    )

    time_dimension = routing.GetDimensionOrDie('Time')
    # [END time_constraint]

    # [START require the least doable stops per node]
    for node in list(range(1, len(data['distance_matrix']))):
        routing.AddDisjunction([manager.NodeToIndex(node)], 100_100)
    # [END require the least doable stops per node]

    # [START add vehicle shifts]
    for vehicle_idx in range(data['num_vehicles']):
        shift_start = data["vehicle_shifts"][vehicle_idx][0]
        shift_end = data["vehicle_shifts"][vehicle_idx][1]
        time_dimension.CumulVar(routing.Start(vehicle_idx)).SetRange(shift_start, shift_end)
        time_dimension.CumulVar(routing.End(vehicle_idx)).SetRange(shift_start, shift_end)
    # [END add vehicle shifts]

    # Instantiate route start and end times to produce feasible times.
    # [START depot_start_end_times]
    for i in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))
    # [END depot_start_end_times]

    # Setting first solution heuristic.
    # [START parameters]
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1)
    # [END parameters]

    # Solve the problem.
    # [START solve]
    solution = routing.SolveWithParameters(search_parameters)
    # [END solve]

    # Print solution on console.
    # [START print_solution]
    if solution:
        print_solution(data, manager, routing, solution)
    # [END print_solution]


if __name__ == "__main__":
    main()
    # [END program]