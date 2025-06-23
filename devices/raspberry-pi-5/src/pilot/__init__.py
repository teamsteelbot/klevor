"""
serial_incoming_messages_queue (Queue): Queue to hold incoming messages from the serial port.
            serial_outgoing_messages_queue (Queue): Queue to hold outgoing messages to the serial port.

        # Initialize the serial dispatcher
        self.__serial_dispatcher = SerialDispatcher(
            serial_incoming_messages_queue, serial_outgoing_messages_queue,
            writer_messages_queue)

after rotation


# Put the parsed line in the server
        if self.__server:
            for angle, measure in self.__distances_dict.items():
                measure_str = str(measure)
                self.__server.broadcast_rplidar_measures(str(measure))

        # Send the measure string to the serial communication
        if self.__serial_communication:
            if self.__challenge == Challenge.WITHOUT_OBSTACLES:
                # Calculate the average front, left and right distances by 5 degrees to each side
                avg_front_dist = self._calculate_average_distance(
                    [*range(355, 360), *range(0, 6)])
                avg_left_dist = self._calculate_average_distance(
                    [*range(265, 276)])
                avg_right_dist = self._calculate_average_distance(
                    [*range(85, 96)])

                # Create a dictionary with the average distances
                avg_distances = {
                    RPLIDARKey.FRONT: avg_front_dist,
                    RPLIDARKey.LEFT: avg_left_dist,
                    RPLIDARKey.RIGHT: avg_right_dist
                }

                # Send the average distances to the serial communication
                self.__serial_communication.send_rplidar_measures(avg_distances)
"""