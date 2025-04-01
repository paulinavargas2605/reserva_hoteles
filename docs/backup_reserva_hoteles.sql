/*
SQLyog Ultimate v11.11 (64 bit)
MySQL - 8.3.0 : Database - reserva_hoteles
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`reserva_hoteles` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `reserva_hoteles`;

/*Table structure for table `habitaciones_hotel` */

DROP TABLE IF EXISTS `habitaciones_hotel`;

CREATE TABLE `habitaciones_hotel` (
  `id_habitacion_hotel` int NOT NULL AUTO_INCREMENT,
  `id_hotel` int DEFAULT NULL,
  `cupo_personas` int DEFAULT NULL,
  `id_t_habitacion` int DEFAULT NULL,
  `total_habitaciones` int DEFAULT NULL,
  `habitaciones_disponibles` int DEFAULT NULL,
  PRIMARY KEY (`id_habitacion_hotel`),
  KEY `fk_hotel` (`id_hotel`),
  KEY `fk_habitacion` (`id_t_habitacion`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `habitaciones_hotel` */

LOCK TABLES `habitaciones_hotel` WRITE;

insert  into `habitaciones_hotel`(`id_habitacion_hotel`,`id_hotel`,`cupo_personas`,`id_t_habitacion`,`total_habitaciones`,`habitaciones_disponibles`) values (1,1,4,1,30,26),(2,1,4,2,3,3),(3,2,6,2,20,20),(4,2,6,3,2,1),(5,3,8,1,10,10),(6,3,8,2,1,0),(7,4,6,1,20,20),(8,4,6,2,20,14),(9,4,6,3,2,2);

UNLOCK TABLES;

/*Table structure for table `hoteles` */

DROP TABLE IF EXISTS `hoteles`;

CREATE TABLE `hoteles` (
  `id_hotel` int NOT NULL AUTO_INCREMENT,
  `sede` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id_hotel`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `hoteles` */

LOCK TABLES `hoteles` WRITE;

insert  into `hoteles`(`id_hotel`,`sede`) values (1,'Barranquilla'),(2,'Cali'),(3,'Cartagena'),(4,'Bogota');

UNLOCK TABLES;

/*Table structure for table `reservas` */

DROP TABLE IF EXISTS `reservas`;

CREATE TABLE `reservas` (
  `id_reserva` int NOT NULL AUTO_INCREMENT,
  `id_habitacion_hotel` int DEFAULT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `cant_habitaciones` int DEFAULT NULL,
  `num_personas` int DEFAULT NULL,
  PRIMARY KEY (`id_reserva`),
  KEY `fk_habitacion_hotel` (`id_habitacion_hotel`)
) ENGINE=MyISAM AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `reservas` */

LOCK TABLES `reservas` WRITE;

insert  into `reservas`(`id_reserva`,`id_habitacion_hotel`,`fecha_inicio`,`fecha_fin`,`cant_habitaciones`,`num_personas`) values (1,1,'2025-03-27','2025-03-30',1,4),(2,1,'2023-05-01','2023-05-05',1,2),(3,3,'2023-05-01','2023-05-05',1,20),(4,3,'2023-05-25','2023-05-26',1,255),(5,3,'2023-05-25','2023-05-26',1,255),(6,6,'2023-05-25','2023-05-26',1,255),(7,1,'2023-06-04','2023-06-05',1,4),(8,4,'2023-06-04','2023-06-05',3,4),(9,8,'2023-06-04','2023-06-05',3,4),(10,8,'2023-06-06','2023-06-07',3,2);

UNLOCK TABLES;

/*Table structure for table `tipo_habitaciones` */

DROP TABLE IF EXISTS `tipo_habitaciones`;

CREATE TABLE `tipo_habitaciones` (
  `id_t_habitaciones` int NOT NULL AUTO_INCREMENT,
  `tipo_habitacion` varchar(20) DEFAULT NULL,
  `tarifa` int DEFAULT NULL,
  PRIMARY KEY (`id_t_habitaciones`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `tipo_habitaciones` */

LOCK TABLES `tipo_habitaciones` WRITE;

insert  into `tipo_habitaciones`(`id_t_habitaciones`,`tipo_habitacion`,`tarifa`) values (1,'Estandar',50000),(2,'Premium',100000),(3,'VIP',150000);

UNLOCK TABLES;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
