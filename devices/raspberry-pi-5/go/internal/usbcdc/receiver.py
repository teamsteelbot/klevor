	@final
	def _open_port(self, port: str) -> None:
		try:
			# Create a new Serial instance for the console port
			self.__console_serial = Serial(
				port,
				self.__baudrate,
				timeout=self.READ_TIMEOUT,
				)
			self.__console_port = port
			self.__console_serial.flush()

		except Exception as e:
			raise RuntimeError(f"Error opening console port {port}: {e}")

	@final
	def _start(self) -> None:
		with self.__rlock:
			# Check if the stop event is set
			if self.__stop_event.is_set():
				raise RuntimeError(
					"Stop event is set. Serial communication receiver will not run.",
					)

			# Check if the serial communication receiver is already running
			if self.__started_event.is_set():
				raise RuntimeError(
					"Serial communication receiver is already running. Cannot start again.",
					)

			# Set the started event
			self.__started_event.set()

		# Open the console port
		for i in range(CONNECTION_ATTEMPTS):
			for port in self.__console_ports:
				try:
					self._open_port(port)

					# Log
					self.__logger.info(
						f"Console port opened on {self.__console_port} after {i + 1} {'attempts' if i != 0 else 'attempt'}.",
						)
					return

				except Exception:
					pass

			sleep(ATTEMPTS_DELAY)

		raise RuntimeError(
			f"Failed to open console port after {CONNECTION_ATTEMPTS} attempts.",
			)

	@final
	def _stop(self) -> None:
		with self.__rlock:
			try:
				# Check if the start event is set
				if self.__started_event.is_set():
					# Clear the started event
					self.__started_event.clear()

					# Wait for the stop sent event to be set
					if not self.__stop_sent_event.wait(timeout=STOP_TIMEOUT):
						self.__logger.warning(
							"Stop sent event not set within timeout. ",
							)
					else:
						# Log the stop sent
						self.__logger.info(
							"Stop sent event set.",
							)

					# Clear the stop sent event
					self.__stop_sent_event.clear()

					# Set the stop waiting confirmation event
					self.__stop_waiting_confirmation_event.set()

					# Wait for the stop confirmation event to be set
					self._wait_confirmation_message(
						STOP_MESSAGE,
						attempts=STOP_TIMEOUT / self.INCOMING_DELAY,
						)

					# Set the stop confirmation event
					self.__stop_confirmation_event.set()

					# Clear the stop waiting confirmation event
					self.__stop_waiting_confirmation_event.clear()

			except Exception as e:
				# Log the error
				self.__logger.error(
					f"Error while stopping the serial communication receiver: {e}",
					)

			# Set the stop event
			self.__stop_event.set()

			# Clear the deleted event
			self.__deleted_event.clear()

			# Close the console serial port
			if self.__console_serial and self.__console_serial.is_open:
				self.__logger.info(
					f"Closing console serial port: {self.__console_port}",
					)
				self.__console_serial.close()
				self.__console_serial = None

		# Log
		self.__logger.info("Stopped.")

	@final
	def _receive_latest_message(self) -> (IncomingMessage | None):
		if self.__console_serial.in_waiting == 0:
			sleep(self.INCOMING_DELAY)
			return None

		# Parse the message from the serial port
		buffer = ""
		while (
				not self.__stop_event.is_set() and not self.__deleted_event.is_set()) or self.__stop_waiting_confirmation_event.is_set():
			data = self.__console_serial.read(1).decode(
				ENCODE,
				errors="ignore",
				)
			if not data:
				continue
			if data == END_CHAR:
				break
			buffer += data

		# Check if the stop event is set or the deleted event is set
		if (
				self.__stop_event.is_set() or self.__deleted_event.is_set()) and not self.__stop_waiting_confirmation_event.is_set():
			return None

		# If the buffer is empty, return None
		if not buffer:
			return None

		# Strip the buffer to remove any leading or trailing whitespace and convert it to a string
		msg_str = buffer.strip()

		# Log
		# self.__logger.debug(f"Received message: '{msg_str}'")

		# Get the message from the string
		msg = IncomingMessage.from_string(msg_str)

		# Check if it's a debug message
		if msg.is_debug():
			# Log the debug message
			self.__logger.debug(
				f"Received debug message: {msg.content}",
				)
			return None

		# If the server is set, send the message to the server
		self.__server_dispatcher.broadcast_serial_incoming_message(
			msg_str,
			) if self.__server_dispatcher else None

		return msg

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