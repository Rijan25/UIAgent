import { useState, useMemo } from 'react';
import { Tabs, Row, Col, Input, Select, Button, ConfigProvider, message as antdMessage } from 'antd';
import type { CSSProperties } from 'react';

export default function GeneratedApp() {
  const [messageApi, contextHolder] = antdMessage.useMessage();

  const [activeTab, setActiveTab] = useState<string>('vendor_configuration');
  const [orderSpecialist, setOrderSpecialist] = useState<string | null>(null);
  const [uodType, setUodType] = useState<'CASE' | 'PALLET' | 'CONTAINER' | null>(null);
  const [poScheduleDays, setPoScheduleDays] = useState<string | null>(null);
  const [containerLoading, setContainerLoading] = useState<'FCL' | 'MIX' | 'CL' | null>(null);
  const [containerSize, setContainerSize] = useState<'10 wheeler' | '20 wheeler' | '40 wheeler' | null>(null);
  const [containerStacking, setContainerStacking] = useState<'Floor Stack' | 'Palletized' | null>(null);
  const [combinedStoreSafetyStock, setCombinedStoreSafetyStock] = useState<number | null>(null);
  const [dcSafetyStocks, setDcSafetyStocks] = useState<number | null>(null);
  const [leadTimeDays, setLeadTimeDays] = useState<number | null>(null);
  const [multiplierDays, setMultiplierDays] = useState<number | null>(null);
  const [unitsPerCase, setUnitsPerCase] = useState<number | null>(null);
  const [casePerContainer, setCasePerContainer] = useState<number | null>(null);
  const [unitsPerContainer, setUnitsPerContainer] = useState<number | null>(null);
  const [cbmPerCase, setCbmPerCase] = useState<number | null>(null);
  const [cbmPerContainer, setCbmPerContainer] = useState<number | null>(null);
  const [unitsPerPallet, setUnitsPerPallet] = useState<number | null>(null);
  const [casePerPallet, setCasePerPallet] = useState<number | null>(null);
  const [palletsPerContainer, setPalletsPerContainer] = useState<number | null>(null);
  const [weightPerContainer, setWeightPerContainer] = useState<number | null>(null);
  const [weightPerCase, setWeightPerCase] = useState<number | null>(null);
  const [moqInUnits, setMoqInUnits] = useState<number | null>(null);
  const [maxPerContainer, setMaxPerContainer] = useState<number | null>(null);
  const [shelfLife, setShelfLife] = useState<number | null>(null);
  const [caseUPC, setCaseUPC] = useState<string | null>(null);
  const [casesWide, setCasesWide] = useState<number | null>(null);
  const [casesDeep, setCasesDeep] = useState<number | null>(null);
  const [heightLayersHeight, setHeightLayersHeight] = useState<number | null>(null);
  const [casesPerLayer, setCasesPerLayer] = useState<number | null>(null);
  const [casesPerPalletDC, setCasesPerPalletDC] = useState<number | null>(null);
  const [palletWeightKg, setPalletWeightKg] = useState<number | null>(null);
  const [unitsPerPalletCalc, setUnitsPerPalletCalc] = useState<number | null>(null);
  const [totalSafetyStock, setTotalSafetyStock] = useState<number | null>(null);

  const unitsPerContainerCalc = useMemo(() => {
    const upc = unitsPerCase;
    const cpc = casePerContainer;
    if (upc !== null && cpc !== null && !isNaN(upc) && !isNaN(cpc)) {
      return upc * cpc;
    }
    return null;
  }, [unitsPerCase, casePerContainer]);

  const cbmPerContainerCalc = useMemo(() => {
    const cbmCase = cbmPerCase;
    const cpc = casePerContainer;
    if (cbmCase !== null && cpc !== null && !isNaN(cbmCase) && !isNaN(cpc)) {
      return cbmCase * cpc;
    }
    return null;
  }, [cbmPerCase, casePerContainer]);

  const casesPerLayerCalc = useMemo(() => {
    const wide = casesWide;
    const deep = casesDeep;
    if (wide !== null && deep !== null && !isNaN(wide) && !isNaN(deep)) {
      return wide * deep;
    }
    return null;
  }, [casesWide, casesDeep]);

  const casesPerPalletDCCalc = useMemo(() => {
    const cpl = casesPerLayer;
    const height = heightLayersHeight;
    if (cpl !== null && height !== null && !isNaN(cpl) && !isNaN(height)) {
      return cpl * height;
    }
    return null;
  }, [casesPerLayer, heightLayersHeight]);

  const unitsPerPalletCalc2 = useMemo(() => {
    const upc = unitsPerCase;
    const cppdc = casesPerPalletDC;
    if (upc !== null && cppdc !== null && !isNaN(upc) && !isNaN(cppdc)) {
      return upc * cppdc;
    }
    return null;
  }, [unitsPerCase, casesPerPalletDC]);

  const totalSafetyStockCalc = useMemo(() => {
    const combined = combinedStoreSafetyStock;
    const dc = dcSafetyStocks;
    const combinedVal = combined !== null && !isNaN(combined) ? combined : 0;
    const dcVal = dc !== null && !isNaN(dc) ? dc : 0;
    return combinedVal + dcVal;
  }, [combinedStoreSafetyStock, dcSafetyStocks]);

  const handleTabChange = (activeKey: string) => {
    setActiveTab(activeKey);
  };

  const handleOrderSpecialistChange = (value: string) => {
    setOrderSpecialist(value);
  };

  const handleUodTypeChange = (value: 'CASE' | 'PALLET' | 'CONTAINER') => {
    setUodType(value);
  };

  const handlePoScheduleDaysChange = (value: string) => {
    setPoScheduleDays(value);
  };

  const handleContainerLoadingChange = (value: 'FCL' | 'MIX' | 'CL') => {
    setContainerLoading(value);
  };

  const handleContainerSizeChange = (value: '10 wheeler' | '20 wheeler' | '40 wheeler') => {
    setContainerSize(value);
  };

  const handleContainerStackingChange = (value: 'Floor Stack' | 'Palletized') => {
    setContainerStacking(value);
  };

  const handleUnitsPerCaseChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setUnitsPerCase(isNaN(val) ? null : val);
    const localUpc = isNaN(val) ? null : val;
    const localCpc = casePerContainer;
    if (localUpc !== null && localCpc !== null && !isNaN(localUpc) && !isNaN(localCpc)) {
      setUnitsPerContainer(localUpc * localCpc);
    }
  };

  const handleCasePerContainerChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setCasePerContainer(isNaN(val) ? null : val);
    const localCpc = isNaN(val) ? null : val;
    const localUpc = unitsPerCase;
    const localCbm = cbmPerCase;
    if (localUpc !== null && localCpc !== null && !isNaN(localUpc) && !isNaN(localCpc)) {
      setUnitsPerContainer(localUpc * localCpc);
    }
    if (localCbm !== null && localCpc !== null && !isNaN(localCbm) && !isNaN(localCpc)) {
      setCbmPerContainer(localCbm * localCpc);
    }
  };

  const handleCbmPerCaseChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setCbmPerCase(isNaN(val) ? null : val);
    const localCbm = isNaN(val) ? null : val;
    const localCpc = casePerContainer;
    if (localCbm !== null && localCpc !== null && !isNaN(localCbm) && !isNaN(localCpc)) {
      setCbmPerContainer(localCbm * localCpc);
    }
  };

  const handleCasesWideChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setCasesWide(isNaN(val) ? null : val);
    const localWide = isNaN(val) ? null : val;
    const localDeep = casesDeep;
    if (localWide !== null && localDeep !== null && !isNaN(localWide) && !isNaN(localDeep)) {
      const newCpl = localWide * localDeep;
      setCasesPerLayer(newCpl);
      const localHeight = heightLayersHeight;
      if (localHeight !== null && !isNaN(localHeight)) {
        setCasesPerPalletDC(newCpl * localHeight);
      }
    }
  };

  const handleCasesDeepChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setCasesDeep(isNaN(val) ? null : val);
    const localDeep = isNaN(val) ? null : val;
    const localWide = casesWide;
    if (localWide !== null && localDeep !== null && !isNaN(localWide) && !isNaN(localDeep)) {
      const newCpl = localWide * localDeep;
      setCasesPerLayer(newCpl);
      const localHeight = heightLayersHeight;
      if (localHeight !== null && !isNaN(localHeight)) {
        setCasesPerPalletDC(newCpl * localHeight);
      }
    }
  };

  const handleHeightLayersHeightChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setHeightLayersHeight(isNaN(val) ? null : val);
    const localHeight = isNaN(val) ? null : val;
    const localCpl = casesPerLayer;
    if (localCpl !== null && localHeight !== null && !isNaN(localCpl) && !isNaN(localHeight)) {
      const newCppdc = localCpl * localHeight;
      setCasesPerPalletDC(newCppdc);
      const localUpc = unitsPerCase;
      if (localUpc !== null && !isNaN(localUpc)) {
        setUnitsPerPalletCalc(localUpc * newCppdc);
      }
    }
  };

  const handleDcSafetyStocksChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setDcSafetyStocks(isNaN(val) ? null : val);
    const localDc = isNaN(val) ? null : val;
    const localCombined = combinedStoreSafetyStock;
    const combinedVal = localCombined !== null && !isNaN(localCombined) ? localCombined : 0;
    const dcVal = localDc !== null && !isNaN(localDc) ? localDc : 0;
    setTotalSafetyStock(combinedVal + dcVal);
  };

  const handleCombinedStoreSafetyStockChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setCombinedStoreSafetyStock(isNaN(val) ? null : val);
    const localCombined = isNaN(val) ? null : val;
    const localDc = dcSafetyStocks;
    const combinedVal = localCombined !== null && !isNaN(localCombined) ? localCombined : 0;
    const dcVal = localDc !== null && !isNaN(localDc) ? localDc : 0;
    setTotalSafetyStock(combinedVal + dcVal);
  };

  const handleSaveVendorConfiguration = () => {
    messageApi.success('Vendor configuration saved successfully');
  };

  const handleSaveSRConfiguration = () => {
    messageApi.success('S&R configuration saved successfully');
  };

  const handleSaveFulfillment = () => {
    messageApi.success('Fulfillment configuration saved successfully');
  };

  const rootContainerStyle: CSSProperties = {
    height: '100vh',
    width: '100vw',
    overflow: 'auto',
    backgroundColor: '#f0f2f5',
  };

  const tabsStyle: CSSProperties = {
    padding: '24px',
    height: '100%',
  };

  const formContainerStyle: CSSProperties = {
    padding: '24px',
    backgroundColor: '#ffffff',
    borderRadius: '8px',
  };

  const disabledInputStyle: CSSProperties = {
    backgroundColor: '#f5f5f5',
  };

  const saveButtonStyle: CSSProperties = {
    marginTop: '24px',
  };

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#52c41a',
          borderRadius: 8,
        },
      }}
    >
      {contextHolder}
      <div style={rootContainerStyle}>
        <Tabs
          activeKey={activeTab}
          onChange={handleTabChange}
          type="line"
          size="large"
          style={tabsStyle}
        >
          <Tabs.TabPane tab="Vendor Configuration" key="vendor_configuration">
            <div style={formContainerStyle}>
              <Row gutter={[24, 24]}>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Units Per Case*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={unitsPerCase ?? ''}
                      onChange={handleUnitsPerCaseChange}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Case Per Container*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={casePerContainer ?? ''}
                      onChange={handleCasePerContainerChange}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Units Per Container</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={unitsPerContainerCalc ?? ''}
                      disabled
                      style={disabledInputStyle}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>CBM Per Case*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={cbmPerCase ?? ''}
                      onChange={handleCbmPerCaseChange}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>CBM Per Container</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={cbmPerContainerCalc ?? ''}
                      disabled
                      style={disabledInputStyle}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Units Per Pallet*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={unitsPerPallet ?? ''}
                      onChange={(e) => setUnitsPerPallet(parseFloat(e.target.value) || null)}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Case Per Pallet*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={casePerPallet ?? ''}
                      onChange={(e) => setCasePerPallet(parseFloat(e.target.value) || null)}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Pallets Per Container*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={palletsPerContainer ?? ''}
                      onChange={(e) => setPalletsPerContainer(parseFloat(e.target.value) || null)}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Weight Per Container</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={weightPerContainer ?? ''}
                      onChange={(e) => setWeightPerContainer(parseFloat(e.target.value) || null)}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Weight Per Case*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={weightPerCase ?? ''}
                      onChange={(e) => setWeightPerCase(parseFloat(e.target.value) || null)}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>MOQ in Units*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={moqInUnits ?? ''}
                      onChange={(e) => setMoqInUnits(parseFloat(e.target.value) || null)}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Max Per Container*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={maxPerContainer ?? ''}
                      onChange={(e) => setMaxPerContainer(parseFloat(e.target.value) || null)}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Shelf Life (agreed upon arrival)*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={shelfLife ?? ''}
                      onChange={(e) => setShelfLife(parseFloat(e.target.value) || null)}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Case UPC*</label>
                    <Input
                      placeholder="Enter..."
                      type="text"
                      value={caseUPC ?? ''}
                      onChange={(e) => setCaseUPC(e.target.value)}
                    />
                  </div>
                </Col>
              </Row>
              <Button
                type="primary"
                size="large"
                style={saveButtonStyle}
                onClick={handleSaveVendorConfiguration}
              >
                Save
              </Button>
            </div>
          </Tabs.TabPane>

          <Tabs.TabPane tab="S&R Configuration" key="sr_configuration">
            <div style={formContainerStyle}>
              <Row gutter={[24, 24]}>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Cases Wide*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={casesWide ?? ''}
                      onChange={handleCasesWideChange}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Cases Deep*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={casesDeep ?? ''}
                      onChange={handleCasesDeepChange}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Height (layers height)*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={heightLayersHeight ?? ''}
                      onChange={handleHeightLayersHeightChange}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Cases Per Layer</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={casesPerLayerCalc ?? ''}
                      disabled
                      style={disabledInputStyle}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Cases Per Pallet (DC)</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={casesPerPalletDCCalc ?? ''}
                      disabled
                      style={disabledInputStyle}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Pallet Weight (in kg)</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={palletWeightKg ?? ''}
                      disabled
                      style={disabledInputStyle}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Units Per Pallet</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={unitsPerPalletCalc2 ?? ''}
                      disabled
                      style={disabledInputStyle}
                    />
                  </div>
                </Col>
              </Row>
              <Button
                type="primary"
                size="large"
                style={saveButtonStyle}
                onClick={handleSaveSRConfiguration}
              >
                Save
              </Button>
            </div>
          </Tabs.TabPane>

          <Tabs.TabPane tab="Fulfillment" key="fulfillment">
            <div style={formContainerStyle}>
              <Row gutter={[24, 24]}>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Order Specialist*</label>
                    <Select
                      placeholder="Select..."
                      value={orderSpecialist}
                      onChange={handleOrderSpecialistChange}
                      style={{ width: '100%' }}
                      options={[
                        { label: 'Diamond Rijan Pokhrel', value: 'Diamond Rijan Pokhrel' },
                      ]}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>UOD Type*</label>
                    <Select
                      placeholder="Select..."
                      value={uodType}
                      onChange={handleUodTypeChange}
                      style={{ width: '100%' }}
                      options={[
                        { label: 'CASE', value: 'CASE' },
                        { label: 'PALLET', value: 'PALLET' },
                        { label: 'CONTAINER', value: 'CONTAINER' },
                      ]}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>PO Schedule Days*</label>
                    <Select
                      placeholder="Select..."
                      value={poScheduleDays}
                      onChange={handlePoScheduleDaysChange}
                      style={{ width: '100%' }}
                      options={[
                        { label: 'Sunday', value: 'Sunday' },
                        { label: 'Monday', value: 'Monday' },
                        { label: 'Tuesday', value: 'Tuesday' },
                        { label: 'Wednesday', value: 'Wednesday' },
                        { label: 'Thursday', value: 'Thursday' },
                        { label: 'Friday', value: 'Friday' },
                        { label: 'Saturday', value: 'Saturday' },
                      ]}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Container Loading *</label>
                    <Select
                      placeholder="Select..."
                      value={containerLoading}
                      onChange={handleContainerLoadingChange}
                      style={{ width: '100%' }}
                      options={[
                        { label: 'FCL', value: 'FCL' },
                        { label: 'MIX', value: 'MIX' },
                        { label: 'CL', value: 'CL' },
                      ]}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Container Size*</label>
                    <Select
                      placeholder="Select..."
                      value={containerSize}
                      onChange={handleContainerSizeChange}
                      style={{ width: '100%' }}
                      options={[
                        { label: '10 wheeler', value: '10 wheeler' },
                        { label: '20 wheeler', value: '20 wheeler' },
                        { label: '40 wheeler', value: '40 wheeler' },
                      ]}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Container Stacking *</label>
                    <Select
                      placeholder="Select..."
                      value={containerStacking}
                      onChange={handleContainerStackingChange}
                      style={{ width: '100%' }}
                      options={[
                        { label: 'Floor Stack', value: 'Floor Stack' },
                        { label: 'Palletized', value: 'Palletized' },
                      ]}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Combined Store Safety Stock (Units)</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={combinedStoreSafetyStock ?? ''}
                      onChange={handleCombinedStoreSafetyStockChange}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>DC Safety Stocks (Units)*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={dcSafetyStocks ?? ''}
                      onChange={handleDcSafetyStocksChange}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Lead Time Days*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={leadTimeDays ?? ''}
                      onChange={(e) => setLeadTimeDays(parseFloat(e.target.value) || null)}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Total Safety Stock</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={totalSafetyStockCalc ?? ''}
                      disabled
                      style={disabledInputStyle}
                    />
                  </div>
                </Col>
                <Col xs={24} sm={12} md={12} lg={12}>
                  <div>
                    <label>Multiplier (Days)*</label>
                    <Input
                      placeholder="Enter..."
                      type="number"
                      value={multiplierDays ?? ''}
                      onChange={(e) => setMultiplierDays(parseFloat(e.target.value) || null)}
                    />
                  </div>
                </Col>
              </Row>
              <Button
                type="primary"
                size="large"
                style={saveButtonStyle}
                onClick={handleSaveFulfillment}
              >
                Save
              </Button>
            </div>
          </Tabs.TabPane>

          <Tabs.TabPane tab="Allocation" key="allocation">
            <div style={formContainerStyle}>
              <p>Allocation configuration coming soon...</p>
            </div>
          </Tabs.TabPane>

          <Tabs.TabPane tab="Seasonal Safety Stock" key="seasonal_safety_stock">
            <div style={formContainerStyle}>
              <p>Seasonal Safety Stock configuration coming soon...</p>
            </div>
          </Tabs.TabPane>
        </Tabs>
      </div>
    </ConfigProvider>
  );
}
