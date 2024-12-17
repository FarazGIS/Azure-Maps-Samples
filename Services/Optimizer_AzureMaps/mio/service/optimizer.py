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

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math

def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f"Objective: {solution.ObjectiveValue()}")

    # Display dropped nodes.
    dropped_nodes = 'Dropped nodes:'
    for index in range(routing.Size()):
        if routing.IsStart(index) or routing.IsEnd(index):
            continue
        if solution.Value(routing.NextVar(index)) == index:
            dropped_nodes += f' {manager.IndexToNode(index)}'
    dropped_nodes += '\n\n'
    print(dropped_nodes)

    max_route_distance = 0
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        route_distance = 0
        while not routing.IsEnd(index):
            if routing.HasDimension('Time'):
                time_var = routing.GetDimensionOrDie('Time').CumulVar(index)
                plan_output += f" Node: {manager.IndexToNode(index)}, Time: {solution.Value(time_var)}\n"
            else:
                plan_output += f" {manager.IndexToNode(index)} -> "
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
        if routing.HasDimension('Time'):
            time_var = routing.GetDimensionOrDie('Time').CumulVar(index)
            plan_output += f" Node: {manager.IndexToNode(index)}, Time: {solution.Value(time_var)}\n"
        else:
            plan_output += f"{manager.IndexToNode(index)}\n"
        plan_output += f"Distance of the route: {route_distance}m\n"
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    print(f"Maximum of the route distances: {max_route_distance}m")
    # [END solution_printer]


def get_result(data, manager, routing, solution):
    result = {}
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        result[vehicle_id] = []
        while not routing.IsEnd(index):
            result[vehicle_id].append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        result[vehicle_id].append(manager.IndexToNode(index))

    if routing.HasDimension('Time'):

        #Add dropped nodes
        result['droppedNodes'] = []
        for index in range(routing.Size()):
            if routing.IsStart(index) or routing.IsEnd(index):
                continue
            if solution.Value(routing.NextVar(index)) == index:
                result['droppedNodes'].append(manager.IndexToNode(index))

        #Add time
        result['time'] = {}
        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)
            result['time'][vehicle_id] = []
            while not routing.IsEnd(index):
                time_var = routing.GetDimensionOrDie('Time').CumulVar(index)
                result['time'][vehicle_id].append(solution.Value(time_var))
                index = solution.Value(routing.NextVar(index))
            time_var = routing.GetDimensionOrDie('Time').CumulVar(index)
            result['time'][vehicle_id].append(solution.Value(time_var))

    return result


def optimizer(data):
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]),
        data["num_vehicles"],
        data["starts"],
        data["ends"]
    )
    routing = pywrapcp.RoutingModel(manager)
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    dimension_name = "Distance"
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        2000000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name,
    )
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # [START time constraint]
    def time_callback(from_index, to_index):
        service_time_mins = 10 # how long vehicle dwells on the node
        vehicle_speed_kph = 50 # speed of each vehicle

        distance_km = distance_callback(from_index, to_index) * data["distanceUnitToKm"]
        travel_time_mins = (distance_km / vehicle_speed_kph) * 60
        total_time_mins = math.ceil(travel_time_mins + service_time_mins)

        return total_time_mins

    if 'vehicle_shifts' in data:
        time_callback_index = routing.RegisterTransitCallback(time_callback)

        routing.AddDimension(
            time_callback_index,
            0,  # Maximum waiting time vehicle
            20000,  # Maximum time per vehicles
            False,  # Slack (allow waiting time)
            'Time'
        )

        time_dimension = routing.GetDimensionOrDie('Time')

        for node in range(manager.GetNumberOfNodes()):
            if node not in data["ends"]:
                routing.AddDisjunction([manager.NodeToIndex(node)], 100_000)

        for vehicle_idx in range(data['num_vehicles']):
            shift_start = data["vehicle_shifts"][vehicle_idx][0]
            shift_end = data["vehicle_shifts"][vehicle_idx][1]
            time_dimension.CumulVar(routing.Start(vehicle_idx)).SetRange(shift_start, shift_end)
            time_dimension.CumulVar(routing.End(vehicle_idx)).SetRange(shift_start, shift_end)

        for i in range(data['num_vehicles']):
            routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(routing.Start(i)))
            routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(routing.End(i)))
    # [END time constraint]

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1)

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        print_solution(data, manager, routing, solution)
        return get_result(data, manager, routing, solution)

    return {}