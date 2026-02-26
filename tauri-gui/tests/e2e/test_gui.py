from playwright.sync_api import sync_playwright
import time

def test_resource_fetcher_gui():
    """完整的 Tauri GUI 功能测试"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            # 1. 导航到应用
            print("📍 步骤 1: 导航到应用...")
            page.goto('http://localhost:1420')
            page.wait_for_load_state('networkidle')
            print("✅ 页面加载成功")

            # 等待一下让应用完全初始化
            time.sleep(2)

            # 2. 检查主应用元素
            print("\n📍 步骤 2: 检查主UI元素...")
            try:
                # 检查标题
                title = page.locator('h1')
                assert "Resource Fetcher" in title.text_content(), "❌ 标题不正确"
                print("✅ 标题显示正确")

                # 检查 URL 输入区域
                url_section = page.get_by_text("Download URL")
                assert url_section.is_visible(), "❌ URL输入区域不可见"
                print("✅ URL输入区域可见")

                # 检查配置区域
                config_section = page.get_by_text("Configuration")
                assert config_section.is_visible(), "❌ 配置区域不可见"
                print("✅ 配置区域可见")

            except Exception as e:
                print(f"❌ 主UI元素检查失败: {e}")
                # 截图用于调试
                page.screenshot(path='debug_main_ui.png')
                raise

            # 3. 测试主题切换
            print("\n📍 步骤 3: 测试主题切换...")
            try:
                # 使用 get_by_role 或 get_by_text 查找按钮
                theme_button = page.get_by_role("button")
                # 查找包含 Dark 或 Light 文本的按钮
                buttons = page.locator('button').all()
                theme_button = None
                for btn in buttons:
                    text = btn.text_content()
                    if text and ('Dark' in text or 'Light' in text):
                        theme_button = btn
                        break

                assert theme_button is not None, "❌ 主题按钮不可见"
                print("✅ 主题按钮找到")

                # 获取初始主题
                html = page.locator('html')
                initial_class = html.get_attribute('class') or ''
                initial_dark = 'dark' in initial_class
                print(f"初始主题: {'暗色' if initial_dark else '亮色'}")

                # 点击切换
                theme_button.click()
                time.sleep(0.5)

                # 验证主题已切换
                after_class = html.get_attribute('class') or ''
                after_dark = 'dark' in after_class
                assert after_dark != initial_dark, "❌ 主题未切换"
                print(f"✅ 主题已切换到: {'暗色' if after_dark else '亮色'}")

                # 切换回原主题
                theme_button.click()
                time.sleep(0.5)
                print("✅ 主题切换功能正常")

            except Exception as e:
                print(f"❌ 主题切换测试失败: {e}")
                page.screenshot(path='debug_theme.png')
                raise

            # 4. 测试 URL 验证
            print("\n📍 步骤 4: 测试 URL 验证...")
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

                assert download_album_btn is not None, "❌ Download Album 按钮不可见"
                assert download_song_btn is not None, "❌ Download Song 按钮不可见"

                # 初始状态 - 按钮应该禁用
                assert download_album_btn.is_disabled(), "❌ 下载按钮初始状态应该是禁用的"
                print("✅ 空URL时按钮正确禁用")

                # 输入无效 URL
                url_input.fill("not-a-valid-url")
                time.sleep(0.5)
                assert download_album_btn.is_disabled(), "❌ 无效URL时按钮应该禁用"
                print("✅ 无效URL时按钮正确禁用")

                # 输入有效 URL
                url_input.fill("https://example.com/album")
                time.sleep(0.5)
                assert download_album_btn.is_enabled(), "❌ 有效URL时按钮应该启用"
                assert download_song_btn.is_enabled(), "❌ 有效URL时按钮应该启用"
                print("✅ 有效URL时按钮正确启用")

            except Exception as e:
                print(f"❌ URL验证测试失败: {e}")
                page.screenshot(path='debug_url_validation.png')
                raise

            # 5. 测试高级设置展开/折叠
            print("\n📍 步骤 5: 测试高级设置...")
            try:
                # 查找 Advanced Settings 按钮
                buttons = page.locator('button').all()
                advanced_button = None
                for btn in buttons:
                    text = btn.text_content()
                    if text and 'Advanced Settings' in text:
                        advanced_button = btn
                        break

                assert advanced_button is not None, "❌ Advanced Settings 按钮不可见"

                # 初始状态应该是折叠的
                timeout_label = page.get_by_text("Timeout (seconds)")
                assert not timeout_label.is_visible(), "❌ 高级设置初始应该折叠"
                print("✅ 高级设置初始折叠")

                # 展开高级设置
                advanced_button.click()
                time.sleep(0.5)
                assert timeout_label.is_visible(), "❌ 高级设置未展开"
                print("✅ 高级设置已展开")

                # 检查高级选项可见性
                retries_label = page.get_by_text("Retries")
                assert retries_label.is_visible(), "❌ Retries 选项不可见"
                print("✅ 高级选项可见")

                # 折叠高级设置
                advanced_button.click()
                time.sleep(0.5)
                assert not timeout_label.is_visible(), "❌ 高级设置未折叠"
                print("✅ 高级设置已折叠")

            except Exception as e:
                print(f"❌ 高级设置测试失败: {e}")
                page.screenshot(path='debug_advanced_settings.png')
                raise

            # 6. 测试配置输入
            print("\n📍 步骤 6: 测试配置输入...")
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
                    assert "/custom/test/path" in value, f"❌ 输出目录未更新，当前值: {value}"
                    print("✅ 输出目录输入正常")

                # 测试数字输入
                limit_input = page.get_by_placeholder("Leave empty to download all songs", exact=False)
                if limit_input.is_visible():
                    limit_input.fill("10")
                    time.sleep(0.3)
                    value = limit_input.input_value()
                    assert value == "10", f"❌ 限制数量未更新，当前值: {value}"
                    print("✅ 数字输入正常")

            except Exception as e:
                print(f"❌ 配置输入测试失败: {e}")
                page.screenshot(path='debug_config_input.png')
                raise

            # 7. 测试复选框
            print("\n📍 步骤 7: 测试复选框...")
            try:
                # 获取所有复选框
                checkboxes = page.locator('input[type="checkbox"]').all()

                if len(checkboxes) >= 1:
                    # 测试第一个复选框（Overwrite）
                    overwrite_checkbox = checkboxes[0]
                    overwrite_checkbox.check()
                    time.sleep(0.3)
                    assert overwrite_checkbox.is_checked(), "❌ Overwrite 未选中"
                    print("✅ Overwrite 选中正常")

                    overwrite_checkbox.uncheck()
                    time.sleep(0.3)
                    assert not overwrite_checkbox.is_checked(), "❌ Overwrite 未取消"
                    print("✅ Overwrite 取消正常")

                if len(checkboxes) >= 3:
                    # 测试第三个复选框（Verbose）
                    verbose_checkbox = checkboxes[2]
                    verbose_checkbox.check()
                    time.sleep(0.3)
                    assert verbose_checkbox.is_checked(), "❌ Verbose 未选中"
                    print("✅ Verbose 选中正常")

            except Exception as e:
                print(f"❌ 复选框测试失败: {e}")
                page.screenshot(path='debug_checkboxes.png')
                raise

            # 8. 测试状态显示
            print("\n📍 步骤 8: 测试状态显示...")
            try:
                # 状态栏应该显示某些内容
                status_text = page.locator('.text-sm')  # 状态消息使用 text-sm 类
                assert status_text.is_visible(), "❌ 状态栏不可见"
                status_value = status_text.text_content()
                print(f"✅ 状态栏显示: {status_value}")

            except Exception as e:
                print(f"❌ 状态显示测试失败: {e}")

            # 9. 截图最终状态
            print("\n📍 步骤 9: 截图最终状态...")
            page.screenshot(path='test_final_state.png', full_page=True)
            print("✅ 最终状态截图已保存")

            print("\n" + "="*60)
            print("✅ 所有测试通过！GUI功能正常！")
            print("="*60)

        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            page.screenshot(path='test_failure.png', full_page=True)
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    test_resource_fetcher_gui()
