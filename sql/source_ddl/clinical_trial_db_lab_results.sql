DROP TABLE IF EXISTS `lab_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lab_results` (
  `lab_result_id` int NOT NULL AUTO_INCREMENT,
  `visit_id` int NOT NULL,
  `patient_id` int NOT NULL,
  `lab_test_name` varchar(150) DEFAULT NULL,
  `lab_test_code` varchar(50) DEFAULT NULL,
  `result_value` decimal(10,4) DEFAULT NULL,
  `result_unit` varchar(50) DEFAULT NULL,
  `normal_range_low` decimal(10,4) DEFAULT NULL,
  `normal_range_high` decimal(10,4) DEFAULT NULL,
  `is_abnormal` tinyint(1) DEFAULT '0',
  `toxicity_grade` int DEFAULT NULL,
  `lab_panel` varchar(100) DEFAULT NULL,
  `collection_datetime` datetime DEFAULT NULL,
  `result_datetime` datetime DEFAULT NULL,
  `lab_vendor` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`lab_result_id`),
  KEY `visit_id` (`visit_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `lab_results_ibfk_1` FOREIGN KEY (`visit_id`) REFERENCES `clinical_visits` (`visit_id`),
  CONSTRAINT `lab_results_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7716 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
