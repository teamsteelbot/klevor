workspace {
    model {
        klevorSystem = softwareSystem "Klevor System" {
            tags "System"
            description "The Klevor System is a software system that manages processes, events, and queues for a robotic platform."

            // Processes
            group "Processes" {
                spawnerProcess = container "Spawner Process" {
                    tags "Process"
                    description "Responsible for spawning and managing other processes."
                }
                writerProcess = container "Writer Process" {
                    tags "Process"
                    description "Handles writing messages."
                }
                serialCommunicationProcess = container "Serial Communication Process" {
                    tags "Process"
                    description "Manages serial communication."
                }
                rplidarProcess = container "RPLidar Process" {
                    tags "Process"
                    description "Handles RPLidar measurements."
                }
                photographerProcess = container "Photographer Process" {
                    tags "Process"
                    description "Captures images and preprocesses them."
                }
                objectDetectorProcess = container "Object Detector Process" {
                    tags "Process"
                    description "Performs object detection on images."
                }
                pilotProcess = container "Pilot Process" {
                    tags "Process"
                    description "Controls the pilot system and integrates data."
                }
            }

            // Events
            group "Events" {
                startEvent = container "Start Event" {
                    tags "Event"
                    description "Signals the start of processes."
                }
                stopEvent = container "Stop Event" {
                    tags "Event"
                    description "Signals the stop of processes."
                }
                writerStopEvent = container "Writer Stop Event" {
                    tags "Event"
                    description "Event to signal the writer process to stop."
                }
                captureImageEvent = container "Capture Image Event" {
                    tags "Event"
                    description "Event to signal when an image should be captured."
                }
            }

            // Values
            group "Values" {
                bno08xYawDegValue = container "BNO08X Yaw Deg Value" {
                    tags "Value"
                    description "Value representing the yaw angle in degrees from the BNO08X sensor."
                }
                bno08xTurnsValue = container "BNO08X Turns Value" {
                    tags "Value"
                    description "Value representing the number of turns from the BNO08X sensor."
                }
            }

            // Queues
            group "Queues" {
                writerMessagesQueue = container "Writer Messages Queue" {
                    tags "Queue"
                    description "Queue for writer messages."
                }
                serialIncomingMessagesQueue = container "Serial Incoming Messages Queue" {
                    tags "Queue"
                    description "Queue for incoming serial messages."
                }
                serialOutgoingMessagesQueue = container "Serial Outgoing Messages Queue" {
                    tags "Queue"
                    description "Queue for outgoing serial messages."
                }
                rplidarMeasuresQueue = container "RPLidar Measures Queue" {
                    tags "Queue"
                    description "Queue for RPLidar measurements."
                }
                photographerImagesQueue = container "Photographer Images Queue" {
                    tags "Queue"
                    description "Queue for captured and preprocessed images."
                }
                objectDetectorInferencesQueue = container "Object Detector Inferences Queue" {
                    tags "Queue"
                    description "Queue for object detection inferences."
                }
            }
        }

        klevorSystemProcesses = softwareSystem "Klevor System Processes" {
            tags "Processes"
            description "Contains all processes of the Klevor System."
        }

        klevorSystemEvents = softwareSystem "Klevor System Events" {
            tags "Events"
            description "Contains all events of the Klevor System."
        }

        klevorSystemValues = softwareSystem "Klevor System Values" {
            tags "Values"
            description "Contains all values of the Klevor System."
        }

        klevorSystemQueues = softwareSystem "Klevor System Queues" {
            tags "Queues"
            description "Contains all queues of the Klevor System."
        }

        // Spawns relationships
        spawnerProcess -> writerProcess "Spawns" {
            tags "Spawns"
        }
        spawnerProcess -> serialCommunicationProcess "Spawns" {
            tags "Spawns"
        }
        spawnerProcess -> rplidarProcess "Spawns" {
            tags "Spawns"
        }
        spawnerProcess -> photographerProcess "Spawns" {
            tags "Spawns"
        }
        spawnerProcess -> objectDetectorProcess "Spawns" {
            tags "Spawns"
        }
        spawnerProcess -> pilotProcess "Spawns" {
            tags "Spawns"
        }

        // Start event relationships
        serialCommunicationProcess -> startEvent "Triggers start event" {
            tags "Triggers"
        }
        rplidarProcess -> startEvent "Signals start" {
            tags "ListensTo"
        }
        photographerProcess -> startEvent "Signals start" {
            tags "ListensTo"
        }
        objectDetectorProcess -> startEvent "Signals start" {
            tags "ListensTo"
        }
        pilotProcess -> startEvent "Signals start" {
            tags "ListensTo"
        }
        writerProcess -> startEvent "Signals start" {
            tags "ListensTo"
        }

        // Stop event relationships
        pilotProcess -> stopEvent "Triggers stop event" {
            tags "Triggers"
        }
        rplidarProcess -> stopEvent "Signals stop to" {
            tags "ListensTo"
        }
        photographerProcess -> stopEvent "Signals stop to" {
            tags "ListensTo"
        }
        objectDetectorProcess -> stopEvent "Signals stop to" {
            tags "ListensTo"
        }
        pilotProcess -> stopEvent "Signals stop to" {
            tags "ListensTo"
        }
        serialCommunicationProcess -> stopEvent "Signals stop to" {
            tags "ListensTo"
        }

        // Writer stop event relationships
        spawnerProcess -> writerStopEvent "Triggers" {
            tags "Triggers"
        }
        writerProcess -> writerStopEvent "Signals stop to" {
            tags "ListensTo"
        }

        // Capture image event relationships
        pilotProcess -> captureImageEvent "Triggers image capture" {
            tags "Triggers"
        }
        photographerProcess -> captureImageEvent "Listens to image capture" {
            tags "ListensTo"
        }

        // BNO08X yaw degrees value relationships
        pilotProcess -> bno08xYawDegValue "Reads yaw angle from" {
            tags "ReadsFrom"
        }
        serialCommunicationProcess -> bno08xYawDegValue "Sets yaw angle to" {
            tags "WritesTo"
        }

        // BNO08X turns value relationships
        pilotProcess -> bno08xTurnsValue "Reads turns from" {
            tags "ReadsFrom"
        }
        serialCommunicationProcess -> bno08xTurnsValue "Sets turns to" {
            tags "WritesTo"
        }

        // Writer messages queue relationships
        writerProcess -> writerMessagesQueue "Writes messages from" {
            tags "ReadsFrom"
        }
        serialCommunicationProcess -> writerMessagesQueue "Logs messages to" {
            tags "WritesTo"
        }
        rplidarProcess -> writerMessagesQueue "Logs messages to" {
            tags "WritesTo"
        }
        photographerProcess -> writerMessagesQueue "Logs messages to" {
            tags "WritesTo"
        }
        objectDetectorProcess -> writerMessagesQueue "Logs messages to" {
            tags "WritesTo"
        }
        pilotProcess -> writerMessagesQueue "Logs messages to" {
            tags "WritesTo"
        }

        // Serial outgogoing messages queue relationships
        serialCommunicationProcess -> serialOutgoingMessagesQueue "Sends messages from" {
            tags "ReadsFrom"
        }
        pilotProcess -> serialOutgoingMessagesQueue "Writes to" {
            tags "WritesTo"
        }

        // Serial incoming messages queue relationships
        serialCommunicationProcess -> serialIncomingMessagesQueue "Puts messages to" {
            tags "WritesTo"
        }
        pilotProcess -> serialIncomingMessagesQueue "Reads from" {
            tags "ReadsFrom"
        }

        // RPLidar measures queue relationships
        rplidarProcess -> rplidarMeasuresQueue "Writes measurements to" {
            tags "WritesTo"
        }
        pilotProcess -> rplidarMeasuresQueue "Reads measurements from" {
            tags "ReadsFrom"
        }

        // Photographer images queue relationships
        photographerProcess -> photographerImagesQueue "Writes images to" {
            tags "WritesTo"
        }
        objectDetectorProcess -> photographerImagesQueue "Reads images from" {
            tags "ReadsFrom"
        }

        // Object detector inferences queue relationships
        objectDetectorProcess -> objectDetectorInferencesQueue "Writes inferences to" {
            tags "WritesTo"
        }
        pilotProcess -> objectDetectorInferencesQueue "Reads inferences from" {
            tags "ReadsFrom"
        }
    }

    views {
        container klevorSystem {
            autolayout tb 2000 1000
            include *
        }

        container klevorSystemProcesses {
            autolayout tb 1500 800
            include spawnerProcess
            include writerProcess
            include serialCommunicationProcess
            include rplidarProcess
            include photographerProcess
            include objectDetectorProcess
            include pilotProcess
        }

        container klevorSystemEvents {
            autolayout tb 1500 800
            include spawnerProcess
            include writerProcess
            include serialCommunicationProcess
            include rplidarProcess
            include photographerProcess
            include objectDetectorProcess
            include pilotProcess
            include startEvent
            include stopEvent
            include captureImageEvent
            include writerStopEvent
        }

        container klevorSystemValues {
            autolayout tb 1500 800
            include spawnerProcess
            include writerProcess
            include serialCommunicationProcess
            include rplidarProcess
            include photographerProcess
            include objectDetectorProcess
            include pilotProcess
            include bno08xYawDegValue
            include bno08xTurnsValue
        }

        container klevorSystemQueues {
            autolayout tb 1500 800
            include spawnerProcess
            include writerProcess
            include serialCommunicationProcess
            include rplidarProcess
            include photographerProcess
            include objectDetectorProcess
            include pilotProcess
            include writerMessagesQueue
            include serialIncomingMessagesQueue
            include serialOutgoingMessagesQueue
            include rplidarMeasuresQueue
            include photographerImagesQueue
            include objectDetectorInferencesQueue
        }

        styles {
            element "SoftwareSystem" {
                shape box
                background #1168bd
                color #ffffff
                metadata false
            }
            element "Process" {
                shape roundedbox
                // Dark teal
                background #087f5b
                color #ffffff
                metadata false
            }
            element "Queue" {
                shape cylinder
                // Medium teal
                background #20c997
                color #000000
                metadata false
            }
            element "Value" {
                shape cylinder
                // Grape
                background #ae3ec9
                color #000000
                metadata false
            }
            element "Event" {
                shape hexagon
                // Light teal
                background #e6fcf5
                color #000000
                metadata false
            }
            relationship "WritesTo" {
                // Green
                color #37b24d
                thickness 4
            }
            relationship "ReadsFrom" {
                // Red
                color #f03e3e
                thickness 4
            }
            relationship "Triggers" {
                // Blue
                color #1c7ed6
                thickness 6
            }
            relationship "ListensTo" {
                // Orange
                color #f76707
                thickness 6
            }
            relationship "Spawns" {
                // Pink
                color #d6336c
                thickness 8
            }
        }
    }
}