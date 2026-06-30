DROP TABLE IF EXISTS `investigators`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `investigators` (
  `investigator_id` int NOT NULL AUTO_INCREMENT,
  `site_id` int NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `email` varchar(150) DEFAULT NULL,
  `phone` varchar(30) DEFAULT NULL,
  `role` varchar(50) DEFAULT 'Principal Investigator',
  `license_number` varchar(100) DEFAULT NULL,
  `specialty` varchar(100) DEFAULT NULL,
  `cv_version_date` date DEFAULT NULL,
  `gcp_certification_date` date DEFAULT NULL,
  `gcp_expiry_date` date DEFAULT NULL,
  `status` varchar(30) DEFAULT 'Active',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`investigator_id`),
  KEY `site_id` (`site_id`),
  CONSTRAINT `investigators_ibfk_1` FOREIGN KEY (`site_id`) REFERENCES `research_sites` (`site_id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
