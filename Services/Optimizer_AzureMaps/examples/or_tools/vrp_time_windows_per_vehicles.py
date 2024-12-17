from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def create_data_model():
    data = {}
    data['num_locations'] = 6  # Including depot
    data['num_vehicles'] = 1
    data['depot'] = 0
    data['demands'] = [0, 10, 5, 8, 3, 7]  # Demand for each location (including depot)
    data['vehicle_capacity'] = 15  # Capacity of the vehicle
    return data

def create_routing_model(data):
    routing = pywrapcp.RoutingModel(data['num_locations'], data['num_vehicles'], data['depot'])

    # Define capacity dimension
    def demand_callback(from_index, to_index):
        # Returns the demand for the location at index 'to_index'
        return data['demands'][to_index]

    demand_callback_index = routing.RegisterTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # no slack
        [data['vehicle_capacity']] * data['num_vehicles'],  # vehicle capacities
        True,  # start cumul to zero
        'Capacity'
    )

    # Define distance callback (you should implement your own)
    def distance_callback(from_index, to_index):
        # Implement your logic to compute distance between locations
        return your_custom_distance_logic(from_index, to_index)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Set the search parameters (you can adjust these as needed)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    )

    return routing, search_parameters

def main():
    data = create_data_model()
    routing, search_parameters = create_routing_model(data)

    # Solve the problem
    solver = routing.solver()
    solution = solver.SolveWithParameters(search_parameters)

    if solution:
        print_solution(data, routing, solution)
    else:
        print("No solution found !")

def print_solution(data, routing, solution):
    print("Total Distance: {} miles".format(solution.ObjectiveValue()))
    index = routing.Start(0)
    plan_output = "Route:\n"
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += " -> {}".format(index)
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    print(plan_output)
    print("Route distance: {} miles".format(route_distance))

if __name__ == "__main__":
    main()
