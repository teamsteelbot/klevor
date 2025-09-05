package pilot

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"sync"
	"sync/atomic"
	"syscall"
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
	internalclip "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/clip"
	internallog "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/log"
	internalrplidar "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/rplidar"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/usbcdc"
	internalusbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/usbcdc/enums"
	"golang.org/x/sync/errgroup"
)

type (
	// DefaultHandler is the default implementation of the Handler interface
	DefaultHandler struct {
		mutex            sync.Mutex
		loggerProducer          internallog.LoggerProducer
		logger                  internallog.Logger
		rplidarHandler          internalrplidar.Handler
		clipHandler             internalclip.Handler
		usbCDCHandler           internalusbcdc.Handler
		usbCDCSender            internalusbcdc.Sender
		isRunning               atomic.Bool
		servoDirection          ServoDirection
		servoAngle              uint16
		motorDirection          MotorDirection
		motorSpeed              uint16
		rplidarMeasures         *[360]*internal.Measure
		rplidarAverageDistances map[CardinalDirection]float64
		clipClassification      *internal.Classification
		latestUpdateTime        time.Time
		bno08xLastTurns         uint8
		rplidarTurnsCounter     uint8
		closed atomic.Bool
	}
)

// NewDefaultHandler creates a new instance of DefaultHandler
//
// Parameters:
//
// logger: The logger to use for logging messages.
// rplidarHandler: The RPLidar handler to use for getting distance measurements.
// clipHandler: The CLIP handler to use for controlling the robot's movement.
// usbCDCHandler: The USB-CDC handler to use for communication with the robot.
//
// Returns:
//
// A pointer to the newly created DefaultHandler instance, or an error if the handler could not be created.
func NewDefaultHandler(
	logger internallog.Logger,
	rplidarHandler internalrplidar.Handler,
	clipHandler internalclip.Handler,
	usbCDCHandler internalusbcdc.Handler,
) (*DefaultHandler, error) {
	// Check if the logger is nil
	if logger == nil {
		return nil, internallog.ErrNilLogger
	}

	// Check if the RPLiDAR handler is nil
	if rplidarHandler == nil {
		return nil, internalrplidar.ErrNilHandler
	}

	// Check if the CLIP handler is nil
	if clipHandler == nil {
		return nil, internalclip.ErrNilHandler
	}

	// Check if the USB-CDC handler is nil
	if usbCDCHandler == nil {
		return nil, internalusbcdc.ErrNilHandler
	}

	return &DefaultHandler{
		logger:         logger,
		rplidarHandler: rplidarHandler,
		clipHandler:    clipHandler,
		usbCDCHandler:  usbCDCHandler,
	}, nil
}

// IsRunning returns true if the handler is running, false otherwise
//
// Returns:
//
// A boolean indicating if the handler is running
func (h *DefaultHandler) IsRunning() bool {
	return h.isRunning.Load()
}

// setMotorSpeed sets the speed of the motor
//
// Parameters:
//
// speed: The speed to set the motor
// direction: The direction to set the motor
//
// Returns:
//
// An error if the speed could not be set, nil otherwise
func (h *DefaultHandler) setMotorSpeed(
	speed uint16,
	direction MotorDirection,
) error {
	// Update the motor direction and speed
	h.motorDirection = direction
	h.motorSpeed = speed

	// Send the outgoing message to set the motor speed
	if direction == MotorDirectionStop || speed == 0 {
		h.loggerProducer.Info(
			"Setting motor speed to 0, stopping the motor",
		)
		return h.usbCDCSender.SendMessage(
			internalusbcdc.OutgoingMotorSpeedStopMessage,
		)
	}
	if direction == MotorDirectionForward {
		h.loggerProducer.Info(
			fmt.Sprintf(
				"Setting motor speed to %d in forward direction",
				speed,
			),
		)
		return h.usbCDCSender.SendMessage(
			internalusbcdc.NewOutgoingMessageFromUint16Content(
				internalusbcdcenums.OutgoingCategoryMotorSpeedForward,
				speed,
			),
		)
	}
	if direction == MotorDirectionBackward {
		h.loggerProducer.Info(
			fmt.Sprintf(
				"Setting motor speed to %d in backward direction",
				speed,
			),
		)
		return h.usbCDCSender.SendMessage(
			internalusbcdc.NewOutgoingMessageFromUint16Content(
				internalusbcdcenums.OutgoingCategoryMotorSpeedBackward,
				speed,
			),
		)
	}
	return ErrInvalidMotorDirection
}

// setMotorStop stops the motor
//
// Returns:
//
// An error if the motor could not be stopped, nil otherwise
func (h *DefaultHandler) setMotorStop() error {
	return h.setMotorSpeed(0, MotorDirectionStop)
}

// setMotorForward sets the motor speed to forward
//
// Parameters:
//
// speed: The speed to set the motor
//
// Returns:
//
// An error if the speed could not be set, nil otherwise
func (h *DefaultHandler) setMotorForward(speed uint16) error {
	return h.setMotorSpeed(speed, MotorDirectionForward)
}

// setMotorBackward sets the motor speed to backward
//
// Parameters:
//
// speed: The speed to set the motor
//
// Returns:
//
// An error if the speed could not be set, nil otherwise
func (h *DefaultHandler) setMotorBackward(speed uint16) error {
	return h.setMotorSpeed(speed, MotorDirectionBackward)
}

// setServoDirection sets the servo direction
//
// Parameters:
//
// angle: The angle to set the servo
// direction: The direction to set the servo
//
// Returns:
//
// An error if the servo direction could not be set, nil otherwise
func (h *DefaultHandler) setServoDirection(
	angle uint16,
	direction ServoDirection,
) error {
	// Update the servo direction and angle
	h.servoDirection = direction
	h.servoAngle = angle

	// Send the outgoing message to set the angle speed
	if direction == ServoDirectionStraight || angle == 90 {
		h.loggerProducer.Info("Setting servo direction to center")
		return h.usbCDCSender.SendMessage(
			internalusbcdc.OutgoingServoDirectionCenterMessage,
		)
	}
	if direction == ServoDirectionLeft {
		h.loggerProducer.Info(
			fmt.Sprintf("Setting servo direction to left with angle %d", angle),
		)
		return h.usbCDCSender.SendMessage(
			internalusbcdc.NewOutgoingMessageFromUint16Content(
				internalusbcdcenums.OutgoingCategoryServoDirectionToLeft,
				angle,
			),
		)
	}
	if direction == ServoDirectionRight {
		h.loggerProducer.Info(
			fmt.Sprintf(
				"Setting servo direction to right with angle %d",
				angle,
			),
		)
		return h.usbCDCSender.SendMessage(
			internalusbcdc.NewOutgoingMessageFromUint16Content(
				internalusbcdcenums.OutgoingCategoryServoDirectionToRight,
				angle,
			),
		)
	}
	return ErrInvalidServoDirection
}

// setServoToCenter sets the servo to the center position
//
// Returns:
//
// An error if the servo could not be set to center, nil otherwise
func (h *DefaultHandler) setServoToCenter() error {
	return h.setServoDirection(90, ServoDirectionStraight)
}

// setServoToLeft sets the servo to the left direction
//
// Parameters:
//
// angle: The angle to set the servo
//
// Returns:
//
// An error if the servo could not be set to left, nil otherwise
func (h *DefaultHandler) setServoToLeft(angle uint16) error {
	return h.setServoDirection(angle, ServoDirectionLeft)
}

// setServoToRight sets the servo to the right direction
//
// Parameters:
//
// angle: The angle to set the servo
//
// Returns:
//
// An error if the servo could not be set to right, nil otherwise
func (h *DefaultHandler) setServoToRight(angle uint16) error {
	return h.setServoDirection(angle, ServoDirectionRight)
}

// setServoToOppositeDirection sets the servo to the opposite direction
func (h *DefaultHandler) setServoToOppositeDirection() error {
	if h.servoDirection == ServoDirectionRight {
		return h.setServoToLeft(h.servoAngle)
	} else if h.servoDirection == ServoDirectionLeft {
		return h.setServoToRight(h.servoAngle)
	}
	return nil
}

// updateCLIPClassification retrieves the latest CLIP classification
//
// Returns:
//
// A pointer to the classification string, or an error if the classification could not be retrieved
func (h *DefaultHandler) updateCLIPClassification() (
	*internal.Classification,
	error,
) {
	// Update the CLIP classification
	h.clipClassification = h.clipHandler.GetClassification()

	// Get the classification from the CLIP handler
	return h.clipClassification, nil
}

// updateRPLiDARMeasures retrieves the latest RPLiDAR measures
//
// Returns:
//
// A pointer to an array of 360 Measure pointers indexed by angle, or an error if the measures could not be retrieved
func (h *DefaultHandler) updateRPLiDARMeasures() (
	*[360]*internal.Measure,
	error,
) {
	// Update the RPLiDAR measures
	h.rplidarMeasures = h.rplidarHandler.GetMeasures()

	// Get the measures from the RPLiDAR handler
	return h.rplidarMeasures, nil
}

// updateRPLiDARAverageDistances updates the average distances from the RPLiDAR measures
//
// Returns:
//
// An error if the average distances could not be updated, nil otherwise
func (h *DefaultHandler) updateRPLiDARAverageDistances() error {
	// Get the RPLiDAR measures
	measures, err := h.updateRPLiDARMeasures()
	if err != nil {
		return fmt.Errorf(
			"RPLiDAR measures could not be retrieved: %w",
			err,
		)
	}
	if measures == nil {
		return ErrNilRPLiDARMeasures
	}

	// Calculate the average north, west and east distances
	averageDistances, err := CalculateAverageDistances(
		measures,
		AverageAngleWidth,
		CardinalDirections...,
	)
	if err != nil {
		return fmt.Errorf(
			"average distances could not be calculated: %w",
			err,
		)
	}
	h.rplidarAverageDistances = averageDistances
	return nil
}

// getAverageDirectionDistance gets the average distance for a specific direction
//
// Parameters:
//
// direction: The direction to get the average distance for
//
// Returns:
//
// The average distance for the specified direction, or 0.0 if the direction is not found
func (h *DefaultHandler) getAverageDirectionDistance(
	direction CardinalDirection,
) float64 {
	if h.rplidarAverageDistances == nil {
		return 0.0
	}

	// Get the average distance for the specified direction
	distance, ok := h.rplidarAverageDistances[direction]
	if !ok {
		return 0.0
	}
	return distance
}

// challengeWithObstaclesHandler handles the challenge with obstacles
//
// Parameters:
//
// ctx: The context to use for the challenge
//
// Returns:
//
// An error if the challenge could not be handled, nil otherwise
func (h *DefaultHandler) challengeWithObstaclesHandler(ctx context.Context) error {
	for {
		select {
		case <-ctx.Done():
			// Send stop message
			_ = h.usbCDCSender.SendStopMessage()
			return ctx.Err()
		default:
			return ErrNotImplemented
		}
	}
}

// challengeWithoutObstaclesHandler handles the challenge without obstacles
//
// Parameters:
//
// ctx: The context to use for the challenge
//
// Returns:
//
// An error if the challenge could not be handled, nil otherwise
func (h *DefaultHandler) challengeWithoutObstaclesHandler(ctx context.Context) error {
	// Get the rotation completed channel
	rotationCompletedCh := h.rplidarHandler.GetRotationCompletedChannel()

	for !h.IsClosed() {
		select {
		case <-ctx.Done():
			return ctx.Err()
			case <-rotationCompletedCh:
		}
	}
}

// incomingMessagesHandler handles incoming messages from the USB-CDC
//
// Parameters:
//
// ctx: Context for managing cancellation and timeouts.
//
// Returns:
//
// An error if there was an issue handling incoming messages, nil otherwise
func (h *DefaultHandler) incomingMessagesHandler(ctx context.Context) error {
	var

	for !h.IsClosed() {
		select {
		case <-ctx.Done():
			return ctx.Err()
			case
		}
		case
	}
}

	/*
	@final
		   	@log_on_error()
		   	def run(self) -> None:
		   		try:
		   			# Start the serial communication receiver
		   			self._start()

		   			# Wait for the first END_CHAR message to be received to ensure the serial port is ready
		   			self.__logger.info(
		   				f"Waiting for initial {repr(END_CHAR)} message to confirm serial communication is ready...",
		   				)
		   			while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
		   				if self.__console_serial.in_waiting == 0:
		   					sleep(self.INCOMING_DELAY)
		   					continue

		   				# Read a single character from the console
		   				char = self.__console_serial.read(1).decode(
		   					ENCODE,
		   					errors="ignore",
		   					)
		   				if not char:
		   					continue
		   				if char == END_CHAR:
		   					break
		   			if self.__stop_event.is_set() or self.__deleted_event.is_set():
		   				# Stop the serial communication receiver
		   				self._stop()
		   				return

		   			# Log
		   			self.__logger.info(
		   				f"Received initial {repr(END_CHAR)} message. Serial communication is ready.",
		   				)

		   			# Wait for the start message
		   			self.__logger.info(
		   				"Waiting for start event...",
		   				)
		   			while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
		   				try:
		   					msg = self._receive_latest_message()
		   					# If no message is received, continue to wait
		   					if msg is None:
		   						continue

		   				except ValueError as e:
		   					# May receive some garbage data, so we catch the exception
		   					raise RuntimeError(
		   						f"Received invalid message, may be garbage data: '{e}'",
		   						)

		   				if msg.is_error():
		   					raise RuntimeError(
		   						f"Received error message: '{msg.content}'",
		   						)

		   				elif msg.is_challenge():
		   					# Log
		   					self.__logger.info("Received challenge message.")

		   					# Send a confirmation message
		   					self.__serial_dispatcher.send_confirmation_message()

		   					# Set the challenge as an environment variable
		   					with self.__challenge.get_lock():
		   						self.__challenge.value = Challenge.from_string(
		   							msg.content,
		   							).as_char

		   					# Continue to wait for the start event
		   					continue

		   				elif msg.is_start():
		   					# Log
		   					self.__logger.info("Received start event.")

		   					# Check if the challenge is set
		   					if self.__challenge.value == Challenge.NONE.as_char:
		   						raise RuntimeError(
		   							"Challenge not set. Stopping communication.",
		   							)

		   					# Send a confirmation message
		   					self.__serial_dispatcher.send_confirmation_message()

		   					# Set the start event
		   					self.__start_event.set()
		   					break

		   				else:
		   					# Log the received message
		   					self.__logger.debug(
		   						f"Received message while waiting for start event: {msg}",
		   						)

		   			while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
		   				try:
		   					msg = self._receive_latest_message()
		   					if msg is None:
		   						continue

		   				except ValueError as e:
		   					# May signal a bad code on the Pico or garbage data
		   					self.__logger.warning(
		   						f"Received invalid message error, skipping: '{e}'",
		   						)
		   					continue

		   				if msg.is_error():
		   					raise RuntimeError(
		   						f"Received error message: '{msg.content}'",
		   						)

		   				elif msg.is_bno08x_yaw_deg():
		   					# Log
		   					self.__logger.debug(
		   						f"Received BNO08X yaw degrees message: {msg.content}",
		   						)

		   					# Update the BNO08X horizontal axis angle
		   					with self.__bno08x_yaw_deg.get_lock():
		   						self.__bno08x_yaw_deg.value = float(msg.content)

		   				elif msg.is_bno08x_turns():
		   					# Log
		   					self.__logger.debug(
		   						f"Received BNO08X turns message: {msg.content}",
		   						)

		   					# Update the BNO08X turns
		   					with self.__bno08x_turns.get_lock():
		   						self.__bno08x_turns.value = int(msg.content)

		   				else:
		   					# Log the received message
		   					self.__logger.debug(
		   						f"Received message: {msg}",
		   						)

		   			# Stop
		   			self._stop()

		   		except Exception as e:
		   			# Stop the serial communication receiver in case of an exception
		   			self._stop()
		   			raise e


	   def _wait_confirmation_message(
	   			self,
	   			msg_to_confirm: OutgoingMessage,
	   			attempts: int = CONFIRMATION_ATTEMPTS,
	   			) -> None:
	   		"""
	   		Wait for a confirmation message from the serial port.

	   		Args:
	   			msg_to_confirm (OutgoingMessage): The message to confirm.
	   			attempts (int): The number of attempts to wait for the confirmation message.
	   		Raises:
	   			RuntimeError: If the confirmation message is not received within the timeout.
	   		"""
	   		# Log
	   		self.__logger.debug(
	   			f"Waiting confirmation message for: {msg_to_confirm}",
	   			)

	   		# Wait for the confirmation message
	   		i = 0
	   		while i < attempts:
	   			msg = self._receive_latest_message()
	   			if msg is None:
	   				i += 1
	   				continue

	   			if msg.is_error():
	   				raise RuntimeError(
	   					f"Received error message: {msg.content}",
	   					)
	   			elif msg.is_confirmation():
	   				# Log the confirmation message
	   				self.__logger.debug(
	   					f"Received confirmation message: {msg.content}",
	   					)
	   				return

	   			else:
	   				# Log the received message
	   				self.__logger.debug(
	   					f"Received message while waiting for confirmation: {msg}",
	   					)

	   		raise RuntimeError(
	   			f"Confirmation message for {msg_to_confirm} not received within timeout.",
	   			)


	*/
}

// runToWrap is the internal function to run the pilot handler
//
// Parameters:
//
// ctx: Context for managing cancellation and timeouts.
// stopFn: Function to call to stop the pilot handler
//
// Returns:
//
// An error if the pilot could not be run, nil otherwise
func (h *DefaultHandler) runToWrap(ctx context.Context, stopFn func()) error {
	// Initialize BNO08x last turns to 0 and RPLiDAR turns counter to 0
	h.bno08xLastTurns = 0
	h.rplidarTurnsCounter = 0

	// Initialize the USB-CDC sender
	usbCDCSender, err := h.usbCDCHandler.NewSender()
	if err != nil {
		return fmt.Errorf("failed to create USB-CDC sender: %w", err)
	}
	h.usbCDCSender = usbCDCSender

	// Get the start message
}

// Run runs the pilot handler
//
// Returns:
//
// An error if the pilot could not be run, nil otherwise
func (h *DefaultHandler) Run() error {
	h.mutex.Lock()

	// Check if it's already running
	if h.IsRunning() {
		h.mutex.Unlock()
		return ErrHandlerAlreadyRunning
	}
	defer func() {
		h.mutex.Lock()

		// Set running to false
		h.isRunning.Store(false)

		h.mutex.Unlock()
	}()

	// Set running to true
	h.isRunning.Store(true)

	h.mutex.Unlock()

	// Create a logger producer
	loggerProducer, err := h.logger.NewProducer(
		LoggerProducerTag,
	)
	if err != nil {
		return fmt.Errorf("failed to create logger producer: %w", err)
	}
	h.loggerProducer = loggerProducer
	defer h.loggerProducer.Close()

	// Context canceled on SIGINT/SIGTERM.
	ctx, stop := signal.NotifyContext(
		context.Background(),
		os.Interrupt,
		syscall.SIGTERM,
	)

	// Create an error group to manage goroutines
	g := errgroup.Group{}

	// Initialize the logger goroutine
	g.Go(
		func() error {
			return internal.StopContextOnError(ctx, stop, h.logger.Run)
		},
	)

	// Generate the CLIP embeddings
	if err = h.clipHandler.GenerateEmbeddings(); err != nil {
		// Wait for the writer goroutine to finish
		stop()
		if err = g.Wait(); err != nil {
			_, _ = fmt.Fprintf(os.Stderr, "error: %v\n", err)
		}
		return err
	}
	defer stop()

	// Initialize the CLIP goroutine
	g.Go(
		func() error {
			return internal.StopContextOnError(ctx, stop, h.clipHandler.Run)
		},
	)

	// Initialize the RPLiDAR goroutine
	g.Go(
		func() error {
			return internal.StopContextOnError(ctx, stop, h.rplidarHandler.Run)
		},
	)

	// Initialize the USB-CDC goroutine
	g.Go(
		func() error {
			return h.usbCDCHandler.Run(ctx, stop)
		},
	)

	// Initialize the run to wrap goroutine
	g.Go(
		func () error {
			return internallog.LogOnError(
				func() error {
					return h.runToWrap(ctx, stop)
				},
				h.loggerProducer,
			)
		},
	)

	// Wait for the goroutines to finish
	return g.Wait()
}

// Close signals no more senders will send; safe to call multiple times.
func (h *DefaultHandler) Close() {
	h.mutex.Lock()

	// Check if the handler is already closed
	if h.IsClosed() {
		h.mutex.Unlock()
		return
	}

	// Mark the handler as closed
	h.closed.Store(true)

	h.mutex.Unlock()

	// Close the logger producer
	if h.loggerProducer != nil {
		h.loggerProducer.Close()
	}

	// Close the USB-CDC sender
	if h.usbCDCSender != nil {
		h.usbCDCSender.Close()
	}
}

// IsClosed returns true if the outgoing messages channel has been closed.
//
// Returns:
//
// True if the outgoing messages channel is closed, otherwise false.
func (h *DefaultHandler) IsClosed() bool {
	return h.closed.Load()
}

/*
		while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
			# Get the start time
			start_time = monotonic()

			# Get the average distances from the RPLidar
			self._update_rplidar_average_distances()
			west_avg_dist = self._get_distance(CardinalDirection.WEST)
			east_avg_dist = self._get_distance(CardinalDirection.EAST)
			north_avg_dist = self._get_distance(CardinalDirection.NORTH)
			north_northeast_avg_dist = self._get_distance(
				CardinalDirection.NORTH_NORTHEAST,
				)
			north_northwest_avg_dist = self._get_distance(
				CardinalDirection.NORTH_NORTHWEST,
				)
			self.__logger.debug(
				f"North: {north_avg_dist}, West: {west_avg_dist}, East: {east_avg_dist}",
				)

			# Check if one of them is 0
			for dist in [
				north_avg_dist, west_avg_dist, east_avg_dist,
				north_northwest_avg_dist, north_northeast_avg_dist,
				]:
				if dist == 0:
					self.__logger.warning(
						"One of the average distances is 0. This may cause unexpected behavior. Waiting for new measures...",
						)

					# Sleep
					self._sleep(start_time)
					continue

			# Check if the front distance is below the safety threshold
			if (north_avg_dist < SAFETY_FRONT_DISTANCE_START_THRESHOLD
					or north_northeast_avg_dist < SAFETY_FRONT_DISTANCE_START_THRESHOLD
					or north_northwest_avg_dist < SAFETY_FRONT_DISTANCE_START_THRESHOLD):
				# Store the current servo angle
				previous_servo_angle = self.__servo_angle
				previous_motor_speed = self.__motor_speed

				# Log the warning
				self.__logger.warning(
					f"Front distance {north_avg_dist} is below the safety threshold.",
					)
				self._set_servo_to_center()
				self._set_motor_backward(MOTOR_SPEED_NORMAL)

				# Sleep for a short time before checking again
				self._sleep(start_time)

				while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
					# Get the average distances again
					self._update_rplidar_average_distances()
					north_avg_dist = self.__average_distances[
						CardinalDirection.NORTH]
					north_northeast_avg_dist = self.__average_distances[
						CardinalDirection.NORTH_NORTHEAST]
					north_northwest_avg_dist = self.__average_distances[
						CardinalDirection.NORTH_NORTHWEST]

					if (north_avg_dist >= SAFETY_FRONT_DISTANCE_STOP_THRESHOLD
							or north_northeast_avg_dist >= SAFETY_FRONT_DISTANCE_STOP_THRESHOLD
							or north_northwest_avg_dist >= SAFETY_FRONT_DISTANCE_STOP_THRESHOLD):
						self.__logger.info(
							"Safety front distance threshold reached",
							)
						break

				# Update the start time
				start_time = monotonic()

				# Set previous servo angle and motor speed back to normal
				if self.__is_turning:
					self._set_servo_angle(previous_servo_angle)
				else:
					self._set_servo_to_opposite(previous_servo_angle)
				self._set_motor_speed(previous_motor_speed)

				# Sleep for a short time before continuing
				self._sleep(start_time)
				continue

			# Check for the current turn and center the servo if necessary
			if self.__is_turning:
				# Check if the front distance is safe to stop turning
				turns = self.__bno08x_turns.value
				if turns > last_turns:
					self.__logger.info(
						f"Detected a turn. Current turns: {turns}, Last turns: {last_turns}",
						)
					self._set_servo_to_center()
					self.__is_turning = False

					# Update for the next check
					last_turns = turns

				elif north_avg_dist >= FRONT_STOP_TURN_DISTANCE_THRESHOLD:
					self.__logger.info(
						"Front distance is safe. Stopping the turning state.",
						)
					self._set_servo_to_center()
					self.__is_turning = False

				# Sleep
				self._sleep(start_time)
				continue

			# Check if it's almost time to stop
			if last_turns >= TURNS or rplidar_turns_counter >= TURNS:
				self._set_servo_to_center()
				self._set_motor_speed(MOTOR_SPEED_NORMAL)

				while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
					# Update the start time
					start_time = monotonic()

					# Get the average distances
					self._update_rplidar_average_distances()
					north_avg_dist = self.__average_distances[
						CardinalDirection.NORTH]

					if north_avg_dist <= STOP_DISTANCE_THRESHOLD:
						# Set the completed event
						self.__completed_event.set()

						# Log the completion message
						self.__logger.info(
							"Challenge completed successfully. Stopping the robot.",
							)
						break

					# Sleep for a short time before checking again
					self._sleep(start_time)
				break

			# Check if the robot should move forward or turn
			if north_avg_dist >= FRONT_START_TURN_DISTANCE_THRESHOLD:
				if (
						north_northeast_avg_dist >= FRONT_START_TURN_DISTANCE_THRESHOLD and
						north_northwest_avg_dist >= FRONT_START_TURN_DISTANCE_THRESHOLD):
					self._set_motor_speed(MOTOR_SPEED_FAST)
				else:
					self._set_motor_speed(MOTOR_SPEED_NORMAL)

				# Check if the servo should make a little turn to the left or right in order to center the robot
				if east_avg_dist >= west_avg_dist * (
						1 + SIDE_DISTANCE_DIFFERENCE_PERCENTAGE):
					self._set_servo_to_right(SERVO_SMALL_TURN_ANGLE)

				elif west_avg_dist >= east_avg_dist * (
						1 + SIDE_DISTANCE_DIFFERENCE_PERCENTAGE):
					self._set_servo_to_left(SERVO_SMALL_TURN_ANGLE)

				else:
					self._set_servo_to_center()

			else:
				self._set_motor_speed(MOTOR_SPEED_NORMAL)

				# Check if the robot should turn left or right based on the side distances
				if east_avg_dist >= SIDE_DISTANCE_THRESHOLD:
					self._set_servo_to_right(SERVO_BIG_TURN_ANGLE)
					self.__is_turning = True

				elif west_avg_dist >= SIDE_DISTANCE_THRESHOLD:
					self._set_servo_to_left(SERVO_BIG_TURN_ANGLE)
					self.__is_turning = True

				if self.__is_turning:
					rplidar_turns_counter += 1

			# Sleep for the calculated delay
			self._sleep(start_time)

		# Update the start time
		start_time = monotonic()

		# Center the servo angle
		self._set_servo_to_center()

		# Stop the motor
		self._set_motor_stop()

		# Sleep for the calculated delay
		self._sleep(start_time)

	@final
	@ignore_sigint
	@log_on_error()
	def run(self):
		# Start the pilot
		self._start()

		# Wait for the start event to be set
		self.__logger.info("Waiting for the start event...")
		while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
			if self.__start_event.wait(timeout=self.START_WAIT_TIMEOUT):
				break
		if self.__stop_event.is_set() or self.__deleted_event.is_set():
			# Stop the Pilot if the stop or deleted event is set
			self._stop()
			return
		self.__logger.info("Started.")

		try:
			# Start the corresponding challenge handler
			if self.__challenge.value == Challenge.WITHOUT_OBSTACLES.as_char:
				self._challenge_without_obstacles()
			elif self.__challenge.value == Challenge.WITH_OBSTACLES.as_char:
				self._challenge_with_obstacles()
			else:
				raise ValueError(
					f"Unknown challenge: {self.__challenge.value}",
					)

			# Stop the Pilot
			self._stop()

		except Exception as e:
			# Stop the Pilot in case of an exception
			self._stop()
			raise e
			)
*/
