DROP TABLE IF EXISTS `vital_signs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vital_signs` (
  `vital_id` int NOT NULL AUTO_INCREMENT,
  `visit_id` int NOT NULL,
  `patient_id` int NOT NULL,
  `measurement_datetime` datetime DEFAULT NULL,
  `systolic_bp` int DEFAULT NULL,
  `diastolic_bp` int DEFAULT NULL,
  `heart_rate` int DEFAULT NULL,
  `temperature_celsius` decimal(4,2) DEFAULT NULL,
  `respiratory_rate` int DEFAULT NULL,
  `oxygen_saturation` decimal(5,2) DEFAULT NULL,
  `weight_kg` decimal(5,2) DEFAULT NULL,
  `notes` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`vital_id`),
  KEY `visit_id` (`visit_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `vital_signs_ibfk_1` FOREIGN KEY (`visit_id`) REFERENCES `clinical_visits` (`visit_id`),
  CONSTRAINT `vital_signs_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1109 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
