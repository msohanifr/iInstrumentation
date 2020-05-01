

DROP TABLE IF EXISTS LANXESS_UAT.dbo.tblDevicePage;
DROP TABLE IF EXISTS LANXESS_UAT.dbo.tblHtml;
DROP TABLE IF EXISTS LANXESS_UAT.dbo.tblProofTest;
DROP TABLE IF EXISTS LANXESS_UAT.dbo.tblDevicePageProoftest;
DROP TABLE IF EXISTS LANXESS_UAT.dbo.tblHtmlTemplateProoftest;
DROP TABLE IF EXISTS LANXESS_UAT.dbo.tblHtmlProofTest;
DROP TABLE IF EXISTS LANXESS_UAT.dbo.tbltext;

DROP TABLE IF EXISTS LANXESS_UAT.dbo.tblAnalyzerConductivity;
DROP TABLE IF EXISTS LANXESS_UAT.dbo.tblPump;
DROP TABLE IF EXISTS LANXESS_UAT.dbo.tblControlValveModulating;
DROP TABLE IF EXISTS LANXESS_UAT.dbo.tlkpControlValveServiceConditions;
DROP TABLE IF EXISTS LANXESS_UAT.dbo.tblSISVerification;
DROP TABLE IF EXISTS LANXESS_UAT.dbo.tblInstrumentation;



/////////////////////////////////////////////////////////////    INSTRUMENT DETAILS   /////////////////////////////////////////

CREATE TABLE LANXESS_UAT.dbo.tblPump(
    /* GENERAL */
                                        PumpKey INT PRIMARY KEY IDENTITY ,
                                        DeviceKey INT NOT NULL REFERENCES LANXESS_UAT.dbo.tblDevice(DeviceKey),
    /* ENVIRONMENT CONDITIONS */
                                        Environment varchar(50),        /* Inside, Outside, Submerged, Hazardous Area, Corrosive Area */
                                        ElectricalClass varchar(50),
                                        ElectricDivision varchar(50),
    /* DEISIGN INFO */
                                        AdjustableSpeedDrive varchar(50),
                                        StandbyPower varchar(50),
                                        Type varchar(50),
                                        DynamicLoad varchar(50),
                                        DriverType varchar(50),
                                        CommoditySG varchar(50),
                                        CenterLineElevation varchar(50),
                                        Size varchar(50),               /* L*W*H */
                                        Weight varchar(50),
                                        InletDiameter varchar(50),
                                        OutletDiameter varchar(50),
                                        NPSH varchar(50),

                                        CapacityMax varchar(50),
                                        CapacityNorm varchar(50),
                                        CapacityMin varchar(50),

                                        TotalHeadMax varchar(50),
                                        TotalHeadNorm varchar(50),
                                        TotalHeadMin varchar(50),

                                        TotalDischargeHeadMax varchar(50),
                                        TotalDischargeHeadNorm varchar(50),
                                        TotalDischargeHEadMin varchar(50),

                                        TotalSuctionHeadMax varchar(50),
                                        TotalSuctionHeadNorm varchar(50),
                                        TotalSuctionHEadMin varchar(50),

                                        PumpSpeedMax varchar(50),
                                        PumpSpeedNorm varchar(50),
                                        PumpSpeedMin varchar(50),

                                        FluidTempMax varchar(50),
                                        FluidTempNorm varchar(50),
                                        FluidTempMin varchar(50),

                                        VapourPressureMax varchar(50),
                                        VapourPressureNorm varchar(50),
                                        VapourPressureMin varchar(50),

                                        SolidsConcentrationMax varchar(50),
                                        SolidsConcentrationNorm varchar(50),
                                        SolidsConcentrationMin varchar(50),

                                        ViscosityMax varchar(50),
                                        ViscosityNorm varchar(50),
                                        ViscosityMin varchar(50),

                                        SealWater BIT,
                                        InstrumentAir BIT,
                                        CoolingWater BIT,
                                        ServiceAir BIT,
                                        CoolingAir BIT,

    /* Electrical */
                                        Power varchar(20),
                                        MotorSpeed varchar(20),
                                        Volts varchar(20),
                                        Phase varchar(20),
                                        MotorEnclosure varchar(50),
                                        MotorFrequency varchar(50),
    /* Manufacturer */
                                        Manufacturer varchar(50),
                                        Model varchar(50),
    /* Construction Materials */
                                        Impeller varchar(50),
                                        RotorStator varchar(50),
                                        Casing varchar(50),
                                        Shaft varchar(50),
                                        ShaftSeal varchar(50),
                                        SealType varchar(50),
                                        WearRings varchar(50),
                                        Bearings varchar(50),
)
CREATE TABLE LANXESS_UAT.dbo.tblAnalyzerConductivity(
    /* GENERAL */
                                                        AnalyzerKey INT PRIMARY KEY IDENTITY ,
                                                        DeviceKey INT NOT NULL REFERENCES LANXESS_UAT.dbo.tblDevice(DeviceKey),
                                                        AreaClassification varchar(50),
                                                        LineMaterial varchar(50),
    /* ELEMENT */
                                                        Type varchar(50),
                                                        Range varchar(50),
                                                        ProbMaxP_at_MaxT varchar(50),
                                                        ProbeConstantLength varchar(50),
                                                        ProcessConnection varchar(50),
                                                        ElementInstallation varchar(50),
                                                        CleaningJetRequiredModel varchar(50),
                                                        ProbeBodyMaterial varchar(50),
                                                        InsertionKit varchar(50),
                                                        CableLength varchar(50),
                                                        CableConnection varchar(50),
                                                        TemperatureCompensation varchar(50),
                                                        ModelNo varchar(50),
    /* TRANSMITTER */
                                                        Calibration varchar(50),
                                                        OutputSignal varchar(50),
                                                        Accuracy varchar(50),
                                                        PowerSupply varchar(50),
                                                        SmartCommunication varchar(50),
                                                        TransmitterInstallation varchar(50),
                                                        CaseMaterial varchar(50),
                                                        Indicator varchar(50),
                                                        CableEntrySize varchar(50),
                                                        AmbientTLimits varchar(50),
    /* FLUID DATA */
                                                        FluidCode varchar(50),
                                                        FluidDescription varchar(50),
                                                        CondMin varchar(20),
                                                        CondMax varchar(20),
                                                        SpecificGravity varchar(50),
                                                        MaxViscosity varchar(50),
                                                        MaxPressure varchar(50),
                                                        OperationPressure varchar(50),
                                                        MaxT varchar(20),
                                                        OperationT varchar(20),
                                                        MaxPercentSolidsByWeight varchar(20),
                                                        FlowMin varchar(20),
                                                        FlowMax varchar(20),
)
/* Table to implement Service Condition in Control Valve */
CREATE TABLE LANXESS_UAT.dbo.tlkpControlValveServiceConditions(
                                                                  id INT PRIMARY KEY ,
                                                                  MaxFlow varchar(20),
                                                                  NormFlow varchar(20),
                                                                  MinFlow varchar(20),
                                                                  ShutOff varchar(20),
)
CREATE TABLE LANXESS_UAT.dbo.tblControlValveModulating(
    /* GENERAL */
                                                          ValveKey INT PRIMARY KEY IDENTITY ,
                                                          DeviceKey INT NOT NULL REFERENCES LANXESS_UAT.dbo.tblDevice(DeviceKey),
                                                          Service varchar(50),
                                                          FlowRate INT references LANXESS_UAT.dbo.tlkpControlValveServiceConditions(id),
                                                          InletPressureP1 INT NOT NULL references LANXESS_UAT.dbo.tlkpControlValveServiceConditions(id),
                                                          OutletPressureP2 INT NOT NULL references LANXESS_UAT.dbo.tlkpControlValveServiceConditions(id),
                                                          DifferentialPressure INT NOT NULL references LANXESS_UAT.dbo.tlkpControlValveServiceConditions(id),
                                                          InletTemperature  INT NOT NULL references LANXESS_UAT.dbo.tlkpControlValveServiceConditions(id),
                                                          SpecWeight  INT NOT NULL references LANXESS_UAT.dbo.tlkpControlValveServiceConditions(id),
                                                          Viscosity  INT NOT NULL references LANXESS_UAT.dbo.tlkpControlValveServiceConditions(id),
                                                          RequiredCV  INT NOT NULL references LANXESS_UAT.dbo.tlkpControlValveServiceConditions(id),
                                                          Travel  INT NOT NULL references LANXESS_UAT.dbo.tlkpControlValveServiceConditions(id),
                                                          Compressibility  INT NOT NULL references LANXESS_UAT.dbo.tlkpControlValveServiceConditions(id),
                                                          SolidConc INT NOT NULL references LANXESS_UAT.dbo.tlkpControlValveServiceConditions(id),
    /* LINE */
                                                          PipelineSizeIn varchar(20),
                                                          PipelineSizeOut varchar(20),
                                                          PipeSchIn varchar(20),
                                                          PipeSchOut varchar(20),
                                                          Material varchar(20),
    /* VALVE BODY */
                                                          BodyType varchar(50),
                                                          BodySize varchar(50),
                                                          BodyStd varchar(50),
                                                          BodyValveMaxPT varchar(50),
                                                          BodyManufacturer varchar(50),
                                                          BodyModel varchar(50),
                                                          BodyMaterial varchar(50),
                                                          BodyLinerMaterial varchar(50),
                                                          LinerMaterialInDiameter varchar(50),
                                                          EndConnectionIn varchar(50),
                                                          EndConnectionOut varchar(50),
                                                          FlangeFaceFinish varchar(50),
                                                          FaceToFaceDim varchar(50),
                                                          EndExtMaterial varchar(50),
                                                          FlowDirection varchar(50),
                                                          TypeOfBonnet varchar(50),
                                                          LubeIsoValve varchar(50),
                                                          Lube varchar(50),
                                                          PackingMaterial varchar(50),
                                                          PackingType varchar(50),
    /* TRIM */
                                                          TrimType varchar(50),
                                                          TrimSize varchar(50),
                                                          TrimRatedTravel varchar(50),
                                                          TrimCharacteristic varchar(50),
                                                          TrimBalancedUnbalanced varchar(50),
                                                          TrimRatedCv varchar(50),
                                                          TrimRatedFl varchar(50),
                                                          TrimRatedXt varchar(50),
                                                          TrimPlugMaterial varchar(50),
                                                          TrimSeatMaterial varchar(50),
                                                          TrimCageMaterial varchar(50),
                                                          TrimStemMaterial varchar(50),
    /* Access */
                                                          AccessNECClass varchar(50),
                                                          AccessGroup varchar(50),
                                                          AccessDiv varchar(50),
    /* ACTUATOR */
                                                          ActuatorType varchar(50),
                                                          ActuatorManufacturer varchar(50),
                                                          ActuatorModel varchar(50),
                                                          ActuatorSize varchar(50),
                                                          ActuatorEffArea varchar(50),
                                                          ActuatorAction varchar(50), /* Open-Close-Lock */
                                                          ActuatorMaxAllowablePress varchar(50),
                                                          ActuatorMinRequiredPress varchar(50),
                                                          ActuatorAvailableAirSupplyPressureMax varchar(50),
                                                          ActuatorAvailableAirSupplyPressureMin varchar(50),
                                                          ActuatorBenchRange varchar(50),
                                                          ActuatorOrientation varchar(50),
                                                          ActuatorHandwhType varchar(50),
                                                          ActuatorAirFailureValve varchar(50),
    /* POSITIONER */
                                                          PosInputSignal varchar(50),
                                                          PosType varchar(50),
                                                          PosCommunication varchar(50),
                                                          PosManufacturer varchar(50),
                                                          PosModel varchar(50),
                                                          PosOnIncreasingSignal varchar(50),
                                                          PosGauges varchar(50),
                                                          PositionerGauges BIT,
                                                          PositionerBypass BIT,
                                                          PositionerCamCharact varchar(50),
                                                          PositionerAirportSize varchar(50),
    /* SWITCHES */
                                                          SwitchType varchar(50),
                                                          SwitchQuantity varchar(50),
                                                          SwitchMfrModel varchar(50),
                                                          SwitchNbContacts varchar(50),
                                                          SwitchActuationPoints varchar(50),
    /* AIR SET */
                                                          AirSetModel varchar(50),
                                                          AirSetPressure varchar(50),
                                                          AirSetFilter varchar(50),
                                                          AirSetGauge varchar(50),
    /* TESTS */
                                                          HydroPressure varchar(50),
                                                          AnsiClass varchar(50),
);
CREATE TABLE LANXESS_UAT.dbo.tblInstrumentation(
                                                   InstrumentKey INT PRIMARY KEY IDENTITY,
                                                   DeviceKey INT NOT NULL REFERENCES LANXESS_UAT.dbo.tblDevice(DeviceKey),
                                                   NominalDiameter REAL,
                                                   NominalPressure REAL,
                                                   DesignTemperature REAL,
                                                   InstalationLocation varchar(50),
                                                   OperatingTemperature REAL,
                                                   OperatingPressure REAL,
                                                   OperatingFlow REAL,
                                                   Vendor varchar(50),
                                                   ModelNumber varchar(50),
                                                   PipingClass varchar(50),
                                                   MediumSubstance varchar(50),
                                                   ProcessConnection varchar(50),
                                                   MotorCircuit varchar(50),                                                  /*  MOTOR  */
                                                   MotorPower int,                                                            /*  MOTOR  */
                                                   NominalCurrent int,                                                        /*  MOTOR  */
                                                   Voltage int,                                                               /*  MOTOR  */
                                                   WireCrossSection REAL,
                                                   ValveType varchar(50),                                                     /*  VALVE  */
                                                   SafePosition varchar(50),                                                  /*  VALVE  */
                                                   Feedback varchar(50),
                                                   LastChangedBy varchar(50),
                                                   LastChangedDate date
);

