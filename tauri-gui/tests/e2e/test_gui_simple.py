from playwright.sync_api import sync_playwright
import time
import sys

# 设置 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_resource_fetcher_gui():
    """完整的 Tauri GUI 功能测试"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            # 1. 导航到应用
            print("Step 1: Navigating to application...")
            page.goto('http://localhost:1420')
            page.wait_for_load_state('networkidle')
            print("OK: Page loaded successfully")

            # 等待一下让应用完全初始化
            time.sleep(2)

            # 2. 检查主应用元素
            print("\nStep 2: Checking main UI elements...")
            try:
                # 检查标题
                title = page.locator('h1')
                title_text = title.text_content()
                assert "Resource Fetcher" in title_text, f"Title incorrect: {title_text}"
                print(f"OK: Title is correct - {title_text}")

                # 检查 URL 输入区域
                url_section = page.get_by_text("Download URL")
                assert url_section.is_visible(), "URL input section not visible"
                print("OK: URL input section is visible")

                # 检查配置区域
                config_section = page.get_by_text("Configuration")
                assert config_section.is_visible(), "Configuration section not visible"
                print("OK: Configuration section is visible")

            except Exception as e:
                print(f"FAIL: Main UI elements check failed: {e}")
                # 截图用于调试
                page.screenshot(path='debug_main_ui.png')
                raise

            # 3. 测试主题切换
            print("\nStep 3: Testing theme toggle...")
            try:
                # 使用 get_by_role 或 get_by_text 查找按钮
                buttons = page.locator('button').all()
                theme_button = None
                for btn in buttons:
                    text = btn.text_content()
                    if text and ('Dark' in text or 'Light' in text):
                        theme_button = btn
                        break

                assert theme_button is not None, "Theme button not visible"
                theme_text = theme_button.text_content()
                print(f"OK: Theme button found - {theme_text}")

                # 获取初始主题
                html = page.locator('html')
                initial_class = html.get_attribute('class') or ''
                initial_dark = 'dark' in initial_class
                print(f"Initial theme: {'Dark' if initial_dark else 'Light'}")

                # 点击切换
                theme_button.click()
                time.sleep(0.5)

                # 验证主题已切换
                after_class = html.get_attribute('class') or ''
                after_dark = 'dark' in after_class
                assert after_dark != initial_dark, "Theme did not switch"
                print(f"OK: Theme switched to: {'Dark' if after_dark else 'Light'}")

                # 切换回原主题
                theme_button.click()
                time.sleep(0.5)
                print("OK: Theme toggle functionality works")

            except Exception as e:
                print(f"FAIL: Theme toggle test failed: {e}")
                page.screenshot(path='debug_theme.png')
                raise

            # 4. 测试 URL 验证
            print("\nStep 4: Testing URL validation...")
            try:
                url_input = page.get_by_placeholder("Enter album or song URL...")

                # 查找下载按钮
                buttons = page.locator('button').all()
                download_album_btn = None
                download_song_btn = None
                for btn in buttons:
                    text = btn.text_content()
                    if text:
                        if 'Download Album' in text:
                            download_album_btn = btn
                        elif 'Download Song' in text:
                            download_song_btn = btn

                assert download_album_btn is not None, "Download Album button not visible"
                assert download_song_btn is not None, "Download Song button not visible"

                # 初始状态 - 按钮应该禁用
                assert download_album_btn.is_disabled(), "Download button should be disabled initially"
                print("OK: Buttons correctly disabled with empty URL")

                # 输入无效 URL
                url_input.fill("not-a-valid-url")
                time.sleep(0.5)
                assert download_album_btn.is_disabled(), "Buttons should be disabled with invalid URL"
                print("OK: Buttons correctly disabled with invalid URL")

                # 输入有效 URL
                url_input.fill("https://example.com/album")
                time.sleep(0.5)
                assert download_album_btn.is_enabled(), "Buttons should be enabled with valid URL"
                assert download_song_btn.is_enabled(), "Buttons should be enabled with valid URL"
                print("OK: Buttons correctly enabled with valid URL")

            except Exception as e:
                print(f"FAIL: URL validation test failed: {e}")
                page.screenshot(path='debug_url_validation.png')
                raise

            # 5. 测试高级设置展开/折叠
            print("\nStep 5: Testing advanced settings...")
            try:
                # 查找 Advanced Settings 按钮
                buttons = page.locator('button').all()
                advanced_button = None
                for btn in buttons:
                    text = btn.text_content()
                    if text and 'Advanced Settings' in text:
                        advanced_button = btn
                        break

                assert advanced_button is not None, "Advanced Settings button not visible"

                # 初始状态应该是折叠的
                timeout_label = page.get_by_text("Timeout (seconds)")
                assert not timeout_label.is_visible(), "Advanced settings should be collapsed initially"
                print("OK: Advanced settings collapsed initially")

                # 展开高级设置
                advanced_button.click()
                time.sleep(0.5)
                assert timeout_label.is_visible(), "Advanced settings did not expand"
                print("OK: Advanced settings expanded")

                # 检查高级选项可见性
                retries_label = page.get_by_text("Retries")
                assert retries_label.is_visible(), "Retries option not visible"
                print("OK: Advanced options visible")

                # 折叠高级设置
                advanced_button.click()
                time.sleep(0.5)
                assert not timeout_label.is_visible(), "Advanced settings did not collapse"
                print("OK: Advanced settings collapsed")

            except Exception as e:
                print(f"FAIL: Advanced settings test failed: {e}")
                page.screenshot(path='debug_advanced_settings.png')
                raise

            # 6. 测试配置输入
            print("\nStep 6: Testing configuration inputs...")
            try:
                # 展开高级设置
                buttons = page.locator('button').all()
                advanced_button = None
                for btn in buttons:
                    text = btn.text_content()
                    if text and 'Advanced Settings' in text:
                        advanced_button = btn
                        break

                if advanced_button:
                    advanced_button.click()
                    time.sleep(0.5)

                # 测试输出目录输入
                output_dir = page.get_by_placeholder("Downloads", exact=False)
                if output_dir.is_visible():
                    output_dir.fill("/custom/test/path")
                    time.sleep(0.3)
                    # 验证输入值
                    value = output_dir.input_value()
                    assert "/custom/test/path" in value, f"Output directory not updated, current: {value}"
                    print("OK: Output directory input works")

                # 测试数字输入
                limit_input = page.get_by_placeholder("Leave empty to download all songs", exact=False)
                if limit_input.is_visible():
                    limit_input.fill("10")
                    time.sleep(0.3)
                    value = limit_input.input_value()
                    assert value == "10", f"Limit not updated, current: {value}"
                    print("OK: Number input works")

            except Exception as e:
                print(f"FAIL: Configuration input test failed: {e}")
                page.screenshot(path='debug_config_input.png')
                raise

            # 7. 测试复选框
            print("\nStep 7: Testing checkboxes...")
            try:
                # 获取所有复选框
                checkboxes = page.locator('input[type="checkbox"]').all()

                if len(checkboxes) >= 1:
                    # 测试第一个复选框（Overwrite）
                    overwrite_checkbox = checkboxes[0]
                    overwrite_checkbox.check()
                    time.sleep(0.3)
                    assert overwrite_checkbox.is_checked(), "Overwrite checkbox not checked"
                    print("OK: Overwrite checkbox check works")

                    overwrite_checkbox.uncheck()
                    time.sleep(0.3)
                    assert not overwrite_checkbox.is_checked(), "Overwrite checkbox not unchecked"
                    print("OK: Overwrite checkbox uncheck works")

                if len(checkboxes) >= 3:
                    # 测试第三个复选框（Verbose）
                    verbose_checkbox = checkboxes[2]
                    verbose_checkbox.check()
                    time.sleep(0.3)
                    assert verbose_checkbox.is_checked(), "Verbose checkbox not checked"
                    print("OK: Verbose checkbox check works")

            except Exception as e:
                print(f"FAIL: Checkbox test failed: {e}")
                page.screenshot(path='debug_checkboxes.png')
                raise

            # 8. 测试状态显示
            print("\nStep 8: Testing status display...")
            try:
                # 状态栏应该显示某些内容
                status_bar = page.locator('div:has(.text-sm)')
                if status_bar.is_visible():
                    status_text = status_bar.text_content()
                    print(f"OK: Status bar is visible: {status_text}")
                else:
                    print("WARNING: Status bar not found, might be OK")

            except Exception as e:
                print(f"WARNING: Status display test failed: {e}")

            # 9. 截图最终状态
            print("\nStep 9: Taking final state screenshot...")
            page.screenshot(path='test_final_state.png', full_page=True)
            print("OK: Final state screenshot saved")

            print("\n" + "="*60)
            print("SUCCESS: All tests passed! GUI is working correctly!")
            print("="*60)

        except Exception as e:
            print(f"\nFAIL: Test failed: {e}")
            page.screenshot(path='test_failure.png', full_page=True)
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    test_resource_fetcher_gui()
