DROP TABLE IF EXISTS `enrollments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enrollments` (
  `enrollment_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `study_id` int NOT NULL,
  `arm_id` int NOT NULL,
  `site_id` int NOT NULL,
  `investigator_id` int NOT NULL,
  `enrollment_date` date DEFAULT NULL,
  `randomization_date` date DEFAULT NULL,
  `randomization_number` varchar(30) DEFAULT NULL,
  `screening_date` date DEFAULT NULL,
  `eligibility_confirmed` tinyint(1) DEFAULT '1',
  `consent_version` varchar(20) DEFAULT NULL,
  `status` varchar(30) DEFAULT 'Active',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`enrollment_id`),
  KEY `patient_id` (`patient_id`),
  KEY `study_id` (`study_id`),
  KEY `arm_id` (`arm_id`),
  KEY `site_id` (`site_id`),
  KEY `investigator_id` (`investigator_id`),
  CONSTRAINT `enrollments_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`),
  CONSTRAINT `enrollments_ibfk_2` FOREIGN KEY (`study_id`) REFERENCES `clinical_studies` (`study_id`),
  CONSTRAINT `enrollments_ibfk_3` FOREIGN KEY (`arm_id`) REFERENCES `study_arms` (`arm_id`),
  CONSTRAINT `enrollments_ibfk_4` FOREIGN KEY (`site_id`) REFERENCES `research_sites` (`site_id`),
  CONSTRAINT `enrollments_ibfk_5` FOREIGN KEY (`investigator_id`) REFERENCES `investigators` (`investigator_id`)
) ENGINE=InnoDB AUTO_INCREMENT=201 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
