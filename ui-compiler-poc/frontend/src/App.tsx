import { useState, useMemo } from 'react';
import { Button, Tabs, Segmented, Select, Input, Typography, message, ConfigProvider } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import type { CSSProperties } from 'react';

export default function GeneratedApp() {
  const [messageApi, contextHolder] = message.useMessage();

  const [activeTab, setActiveTab] = useState<string>('UI Design');
  const [viewMode, setViewMode] = useState<string>('Generate');
  const [designMode, setDesignMode] = useState<string>('Hifi Designs');
  const [style, setStyle] = useState<string>('');
  const [selectType, setSelectType] = useState<string>('Desktop');
  const [selectFont, setSelectFont] = useState<string>('Inter');
  const [promptText, setPromptText] = useState<string>('');

  const characterCount = useMemo(() => promptText.length, [promptText]);
  const isPromptValid = useMemo(() => promptText.length >= 5, [promptText]);

  const handleClosePanel = () => {
    // Custom close panel logic
  };

  const handleRefresh = () => {
    setPromptText('');
    setDesignMode('Hifi Designs');
    setStyle('');
    setSelectType('Desktop');
    setSelectFont('Inter');
  };

  const handleTryExample = () => {
    setPromptText('Landing page for a job search platform');
  };

  const handleGenerateDesign = () => {
    if (promptText.length < 5) {
      messageApi.error('Failed to generate design. Please try again.');
      return;
    }

    messageApi.loading({ content: 'Generating...', key: 'generate' });
    
    setTimeout(() => {
      messageApi.success({ content: 'Design generated successfully', key: 'generate' });
    }, 1000);
  };

  const rootContainerStyle: CSSProperties = {
    backgroundColor: '#ffffff',
    width: '100%',
    height: '100vh',
    display: 'flex',
    flexDirection: 'column'
  };

  const headerContainerStyle: CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px 20px',
    borderBottom: '1px solid #f0f0f0'
  };

  const logoTextStyle: CSSProperties = {
    fontSize: '14px'
  };

  const btnCloseStyle: CSSProperties = {
    fontSize: '24px',
    padding: '0 8px'
  };

  const navTabsStyle: CSSProperties = {
    paddingLeft: '20px',
    paddingRight: '20px'
  };

  const contentContainerStyle: CSSProperties = {
    padding: '24px 20px',
    flex: 1,
    overflowY: 'auto'
  };

  const titleRowStyle: CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px'
  };

  const titleTextStyle: CSSProperties = {
    margin: 0,
    fontWeight: '700'
  };

  const titleControlsStyle: CSSProperties = {
    display: 'flex',
    gap: '12px',
    alignItems: 'center'
  };

  const formGridStyle: CSSProperties = {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '16px',
    marginBottom: '24px'
  };

  const selectStyle: CSSProperties = {
    width: '100%'
  };

  const promptSectionStyle: CSSProperties = {
    marginBottom: '24px'
  };

  const promptLabelStyle: CSSProperties = {
    display: 'block',
    marginBottom: '8px',
    fontSize: '14px'
  };

  const textareaPromptStyle: CSSProperties = {
    width: '100%',
    marginBottom: '8px'
  };

  const promptFooterStyle: CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  };

  const promptHintStyle: CSSProperties = {
    fontSize: '12px'
  };

  const promptControlsStyle: CSSProperties = {
    display: 'flex',
    gap: '12px',
    alignItems: 'center'
  };

  const btnTryExampleStyle: CSSProperties = {
    fontSize: '12px',
    padding: 0
  };

  const charCounterStyle: CSSProperties = {
    fontSize: '12px'
  };

  const btnGenerateStyle: CSSProperties = {
    background: 'linear-gradient(90deg, #7c3aed 0%, #6d28d9 100%)',
    borderRadius: '24px',
    height: '48px',
    fontWeight: '600',
    fontSize: '16px'
  };

  const tabItems = [
    { key: 'UI Design', label: 'UI Design' },
    { key: 'Diagrams', label: 'Diagrams' },
    { key: 'UX Review', label: 'UX Review' },
    { key: 'Workshops', label: 'Workshops' },
    { key: 'AI Tools', label: 'AI Tools' }
  ];

  const designModeOptions = [
    { value: 'Hifi Designs', label: 'Hifi Designs' },
    { value: 'Wireframes', label: 'Wireframes' }
  ];

  const typeOptions = [
    { value: 'Desktop', label: 'Desktop' },
    { value: 'Mobile', label: 'Mobile' },
    { value: 'Tablet', label: 'Tablet' }
  ];

  const fontOptions = [
    { value: 'Inter', label: 'Inter' },
    { value: 'Roboto', label: 'Roboto' },
    { value: 'Open Sans', label: 'Open Sans' }
  ];

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#7c3aed',
          fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
          borderRadius: 8
        }
      }}
    >
      {contextHolder}
      <div style={rootContainerStyle}>
        <div style={headerContainerStyle}>
          <Typography.Text strong style={logoTextStyle}>
            UXpilot.ai – UX Design & Research
          </Typography.Text>
          <Button
            type="text"
            size="large"
            style={btnCloseStyle}
            onClick={handleClosePanel}
          >
            ×
          </Button>
        </div>

        <Tabs
          activeKey={activeTab}
          items={tabItems}
          onChange={(key) => setActiveTab(key)}
          style={navTabsStyle}
        />

        <div style={contentContainerStyle}>
          <div style={titleRowStyle}>
            <Typography.Title level={3} style={titleTextStyle}>
              Generate Hifi UI & wireframes
            </Typography.Title>
            <div style={titleControlsStyle}>
              <Segmented
                options={['Generate', 'Favorites']}
                value={viewMode}
                onChange={(value) => setViewMode(value as string)}
              />
              <Button
                type="text"
                shape="circle"
                icon={<ReloadOutlined />}
                onClick={handleRefresh}
              />
            </div>
          </div>

          <div style={formGridStyle}>
            <Select
              placeholder="Select design mode"
              options={designModeOptions}
              value={designMode}
              onChange={(value) => setDesignMode(value)}
              style={selectStyle}
              aria-label="design_mode_select"
            />
            <Select
              placeholder="Select style"
              options={[]}
              value={style}
              onChange={(value) => setStyle(value)}
              style={selectStyle}
              aria-label="style_select"
            />
            <Select
              placeholder="Select type"
              options={typeOptions}
              value={selectType}
              onChange={(value) => setSelectType(value)}
              style={selectStyle}
              aria-label="type_select"
            />
            <Select
              placeholder="Select font"
              options={fontOptions}
              value={selectFont}
              onChange={(value) => setSelectFont(value)}
              style={selectStyle}
              aria-label="font_select"
            />
          </div>

          <div style={promptSectionStyle}>
            <Typography.Text strong style={promptLabelStyle}>
              Write prompt
            </Typography.Text>
            <Input.TextArea
              placeholder="Landing page for a job search platform"
              rows={4}
              maxLength={500}
              value={promptText}
              onChange={(e) => setPromptText(e.target.value)}
              style={textareaPromptStyle}
              aria-label="prompt_textarea"
            />
            <div style={promptFooterStyle}>
              <Typography.Text type="secondary" style={promptHintStyle}>
                Min. 5 characters
              </Typography.Text>
              <div style={promptControlsStyle}>
                <Button
                  type="link"
                  size="small"
                  style={btnTryExampleStyle}
                  onClick={handleTryExample}
                >
                  Try example
                </Button>
                <Typography.Text type="secondary" style={charCounterStyle}>
                  {characterCount}
                </Typography.Text>
              </div>
            </div>
          </div>
        </div>

        <Button
          type="primary"
          size="large"
          block
          disabled={!isPromptValid}
          onClick={handleGenerateDesign}
          style={btnGenerateStyle}
        >
          Generate hifi design
        </Button>
      </div>
    </ConfigProvider>
  );
}
