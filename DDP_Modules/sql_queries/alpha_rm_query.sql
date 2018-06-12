select

dosimeterid = d.SerialNumber,
measurementid = rm.MeasurementTransactionID,
measurementtimestamp = rm.MeasurementDate,
c39 = rmv2.Amount,
c40 = rmv3.Amount,
c41 = rmv4.Amount,
c42 = rmv5.Amount,
c43 = rmv6.Amount,
c44 = rmv7.Amount,
c46 = rmv8.Amount,
tempint = rm.InternalTemp,
tempext = rm.ExternalTemp,
motiondetectioncount = rm.MotionDetectionCounter

from

RawMeasurement as rm,
Dosimeters as d,
RawMeasurementValues as rmv1,
RawMeasurementValues as rmv2,
RawMeasurementValues as rmv3,
RawMeasurementValues as rmv4,
RawMeasurementValues as rmv5,
RawMeasurementValues as rmv6,
RawMeasurementValues as rmv7,
RawMeasurementValues as rmv8

where

(	d.DosimeterID = rm.DosimeterID
	and rmv1.RawMeasurementID = rm.RawMeasurementID
	and rmv2.RawMeasurementID = rm.RawMeasurementID
	and rmv3.RawMeasurementID = rm.RawMeasurementID
	and rmv4.RawMeasurementID = rm.RawMeasurementID
	and rmv5.RawMeasurementID = rm.RawMeasurementID
	and rmv6.RawMeasurementID = rm.RawMeasurementID
	and rmv7.RawMeasurementID = rm.RawMeasurementID
	and rmv8.RawMeasurementID = rm.RawMeasurementID
	and rmv1.SensorTypeID = 1
	and rmv2.SensorTypeID = 2
	and rmv3.SensorTypeID = 3
	and rmv4.SensorTypeID = 4
	and rmv5.SensorTypeID = 5
	and rmv6.SensorTypeID = 6
	and rmv7.SensorTypeID = 7
	and rmv8.SensorTypeID = 8
)