DROP TABLE IF EXISTS `drug_administration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drug_administration` (
  `administration_id` int NOT NULL AUTO_INCREMENT,
  `visit_id` int NOT NULL,
  `patient_id` int NOT NULL,
  `enrollment_id` int NOT NULL,
  `medication_id` int NOT NULL,
  `planned_dose` decimal(10,4) DEFAULT NULL,
  `actual_dose` decimal(10,4) DEFAULT NULL,
  `dose_unit` varchar(30) DEFAULT NULL,
  `dose_modification_reason` varchar(300) DEFAULT NULL,
  `administration_datetime` datetime DEFAULT NULL,
  `infusion_duration_mins` int DEFAULT NULL,
  `administered_by` varchar(150) DEFAULT NULL,
  `lot_number` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`administration_id`),
  KEY `visit_id` (`visit_id`),
  KEY `patient_id` (`patient_id`),
  KEY `enrollment_id` (`enrollment_id`),
  KEY `medication_id` (`medication_id`),
  CONSTRAINT `drug_administration_ibfk_1` FOREIGN KEY (`visit_id`) REFERENCES `clinical_visits` (`visit_id`),
  CONSTRAINT `drug_administration_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`),
  CONSTRAINT `drug_administration_ibfk_3` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`),
  CONSTRAINT `drug_administration_ibfk_4` FOREIGN KEY (`medication_id`) REFERENCES `medications` (`medication_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1109 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
