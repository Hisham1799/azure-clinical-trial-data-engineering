DROP TABLE IF EXISTS `study_arms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `study_arms` (
  `arm_id` int NOT NULL AUTO_INCREMENT,
  `study_id` int NOT NULL,
  `arm_name` varchar(100) NOT NULL,
  `arm_code` varchar(20) DEFAULT NULL,
  `description` varchar(500) DEFAULT NULL,
  `arm_type` varchar(50) DEFAULT NULL,
  `planned_subjects` int DEFAULT NULL,
  PRIMARY KEY (`arm_id`),
  KEY `study_id` (`study_id`),
  CONSTRAINT `study_arms_ibfk_1` FOREIGN KEY (`study_id`) REFERENCES `clinical_studies` (`study_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
