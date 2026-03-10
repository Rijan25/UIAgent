import { useState, useMemo } from 'react';
import { ConfigProvider, Tabs, Row, Col, Form, Input, Radio, Select } from 'antd';
import type { CSSProperties } from 'react';

export default function GeneratedApp() {
  const [activeTab, setActiveTab] = useState<string>('vendor');
  const [stackType, setStackType] = useState<'floor_stack' | 'palletize'>('floor_stack');
  const [unitsPerCase, setUnitsPerCase] = useState<number | null>(null);
  const [casePerContainer, setCasePerContainer] = useState<number | null>(null);
  const [cbmPerCase, setCbmPerCase] = useState<number | null>(null);
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
  const [height, setHeight] = useState<number>(8);
  const [casesPerPalletDC, setCasesPerPalletDC] = useState<number | null>(null);
  const [palletWeightKg, setPalletWeightKg] = useState<number>(45);
  const [unitsPerPalletCalc, setUnitsPerPalletCalc] = useState<number>(0);
  const [orderSpecialist, setOrderSpecialist] = useState<string | null>(null);
  const [uodType, setUodType] = useState<string | null>(null);
  const [poScheduleDays, setPoScheduleDays] = useState<string | null>(null);
  const [containerLoading, setContainerLoading] = useState<string | null>(null);
  const [containerSize, setContainerSize] = useState<string | null>(null);
  const [containerStacking, setContainerStacking] = useState<string | null>(null);
  const [combinedStoreSafetyStock, setCombinedStoreSafetyStock] = useState<number | null>(null);
  const [dcSafetyStocks, setDcSafetyStocks] = useState<number | null>(null);
  const [leadTimeDays, setLeadTimeDays] = useState<number | null>(null);
  const [multiplierDays, setMultiplierDays] = useState<number | null>(null);
  const [totalSafetyStock, setTotalSafetyStock] = useState<number | null>(null);

  const unitsPerContainer = useMemo(() => {
    const upc = unitsPerCase;
    const cpc = casePerContainer;
    if (upc !== null && cpc !== null && !isNaN(upc) && !isNaN(cpc)) {
      return upc * cpc;
    }
    return null;
  }, [unitsPerCase, casePerContainer]);

  const cbmPerContainer = useMemo(() => {
    const cbmCase = cbmPerCase;
    const cpc = casePerContainer;
    if (cbmCase !== null && cpc !== null && !isNaN(cbmCase) && !isNaN(cpc)) {
      return cbmCase * cpc;
    }
    return null;
  }, [cbmPerCase, casePerContainer]);

  const casesPerLayer = useMemo(() => {
    const cw = casesWide;
    const h = height;
    if (cw !== null && h !== null && !isNaN(cw) && !isNaN(h)) {
      return cw * h;
    }
    return null;
  }, [casesWide, height]);

  const rootContainerStyle: CSSProperties = {
    width: '100vw',
    height: '100vh',
    backgroundColor: '#f0f5f0',
    padding: '0',
    margin: '0',
    overflow: 'auto',
  };

  const tabsStyle: CSSProperties = {
    width: '100%',
    height: '100%',
    padding: '24px',
  };

  const tabContentStyle: CSSProperties = {
    padding: '24px',
  };

  const disabledInputStyle: CSSProperties = {
    backgroundColor: '#f5f5f5',
  };

  const vendorConfigTab = (
    <div style={tabContentStyle}>
      <Radio.Group
        value={stackType}
        onChange={(e) => setStackType(e.target.value)}
        style={{ marginBottom: '24px' }}
      >
        <Radio value="floor_stack">Floor Stack</Radio>
        <Radio value="palletize">Palletize</Radio>
      </Radio.Group>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Units Per Case*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={unitsPerCase ?? ''}
              onChange={(e) => setUnitsPerCase(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Case Per Container*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={casePerContainer ?? ''}
              onChange={(e) => setCasePerContainer(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Units Per Container" tooltip="Auto-calculated">
            <Input
              placeholder="Enter..."
              disabled
              style={disabledInputStyle}
              value={unitsPerContainer ?? ''}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="CBM Per Case*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={cbmPerCase ?? ''}
              onChange={(e) => setCbmPerCase(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="CBM Per Container" tooltip="Auto-calculated">
            <Input
              placeholder="Enter..."
              disabled
              style={disabledInputStyle}
              value={cbmPerContainer ?? ''}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Units Per Pallet*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={unitsPerPallet ?? ''}
              onChange={(e) => setUnitsPerPallet(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Case Per Pallet*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={casePerPallet ?? ''}
              onChange={(e) => setCasePerPallet(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Pallets Per Container*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={palletsPerContainer ?? ''}
              onChange={(e) => setPalletsPerContainer(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Weight Per Container">
            <Input
              placeholder="Enter..."
              type="number"
              value={weightPerContainer ?? ''}
              onChange={(e) => setWeightPerContainer(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Weight Per Case*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={weightPerCase ?? ''}
              onChange={(e) => setWeightPerCase(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="MOQ in Units*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={moqInUnits ?? ''}
              onChange={(e) => setMoqInUnits(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Max Per Container*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={maxPerContainer ?? ''}
              onChange={(e) => setMaxPerContainer(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Shelf Life (agreed upon arrival)*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={shelfLife ?? ''}
              onChange={(e) => setShelfLife(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Case UPC*" required>
            <Input
              placeholder="Enter..."
              value={caseUPC ?? ''}
              onChange={(e) => setCaseUPC(e.target.value)}
            />
          </Form.Item>
        </Col>
      </Row>
    </div>
  );

  const srConfigTab = (
    <div style={tabContentStyle}>
      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Cases Wide*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={casesWide ?? ''}
              onChange={(e) => setCasesWide(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Cases Deep*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={casesDeep ?? ''}
              onChange={(e) => setCasesDeep(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Height (layers height)*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={height}
              onChange={(e) => setHeight(e.target.value ? Number(e.target.value) : 8)}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Cases Per Layer" tooltip="Auto-calculated: Cases Wide × Height">
            <Input
              placeholder="Enter..."
              disabled
              style={disabledInputStyle}
              value={casesPerLayer ?? ''}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Cases Per Pallet (DC)" tooltip="Auto-calculated">
            <Input
              placeholder="Enter..."
              disabled
              style={disabledInputStyle}
              value={casesPerPalletDC ?? ''}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Pallet Weight (in kg)" tooltip="Auto-calculated">
            <Input
              placeholder="Enter..."
              disabled
              style={disabledInputStyle}
              value={palletWeightKg}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Units Per Pallet" tooltip="Auto-calculated">
            <Input
              placeholder="Enter..."
              disabled
              style={disabledInputStyle}
              value={unitsPerPalletCalc}
            />
          </Form.Item>
        </Col>
      </Row>
    </div>
  );

  const fulfillmentTab = (
    <div style={tabContentStyle}>
      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Order Specialist*" required>
            <Select
              placeholder="Select..."
              value={orderSpecialist}
              onChange={(value) => setOrderSpecialist(value)}
              options={[]}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="UOD Type*" required>
            <Select
              placeholder="Select..."
              value={uodType}
              onChange={(value) => setUodType(value)}
              options={[]}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="PO Schedule Days*" required>
            <Select
              placeholder="Select..."
              value={poScheduleDays}
              onChange={(value) => setPoScheduleDays(value)}
              options={[]}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Container Loading *" required>
            <Select
              placeholder="Select..."
              value={containerLoading}
              onChange={(value) => setContainerLoading(value)}
              options={[]}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Container Size*" required>
            <Select
              placeholder="Select..."
              value={containerSize}
              onChange={(value) => setContainerSize(value)}
              options={[]}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Container Stacking *" required>
            <Select
              placeholder="Select..."
              value={containerStacking}
              onChange={(value) => setContainerStacking(value)}
              options={[]}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Combined Store Safety Stock (Units)" tooltip="Auto-calculated">
            <Input
              placeholder="Enter..."
              disabled
              style={disabledInputStyle}
              value={combinedStoreSafetyStock ?? ''}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="DC Safety Stocks (Units)*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={dcSafetyStocks ?? ''}
              onChange={(e) => setDcSafetyStocks(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Lead Time Days*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={leadTimeDays ?? ''}
              onChange={(e) => setLeadTimeDays(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Total Safety Stock" tooltip="Auto-calculated">
            <Input
              placeholder="Enter..."
              disabled
              style={disabledInputStyle}
              value={totalSafetyStock ?? ''}
            />
          </Form.Item>
        </Col>
        <Col xs={24} sm={12} md={12} lg={12}>
          <Form.Item label="Multiplier (Days)*" required>
            <Input
              placeholder="Enter..."
              type="number"
              value={multiplierDays ?? ''}
              onChange={(e) => setMultiplierDays(e.target.value ? Number(e.target.value) : null)}
            />
          </Form.Item>
        </Col>
      </Row>
    </div>
  );

  const allocationTab = (
    <div style={tabContentStyle}>
      <div>Allocation content placeholder</div>
    </div>
  );

  const seasonalTab = (
    <div style={tabContentStyle}>
      <div>Seasonal Safety Stock content placeholder</div>
    </div>
  );

  const tabItems = [
    {
      key: 'vendor',
      label: 'Vendor Configuration',
      children: vendorConfigTab,
    },
    {
      key: 'sr',
      label: 'S&R Configuration',
      children: srConfigTab,
    },
    {
      key: 'fulfillment',
      label: 'Fulfillment',
      children: fulfillmentTab,
    },
    {
      key: 'allocation',
      label: 'Allocation',
      children: allocationTab,
    },
    {
      key: 'seasonal',
      label: 'Seasonal Safety Stock',
      children: seasonalTab,
    },
  ];

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#52c41a',
          borderRadius: 8,
          fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        },
      }}
    >
      <div style={rootContainerStyle}>
        <Tabs
          activeKey={activeTab}
          onChange={(key) => setActiveTab(key)}
          style={tabsStyle}
          items={tabItems}
        />
      </div>
    </ConfigProvider>
  );
}
