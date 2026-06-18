import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_craft_comparison import run_tests as run_craft_tests
from tests.test_permeability_analysis import run_tests as run_perm_tests
from tests.test_virtual_experience import run_tests as run_virtual_tests


def main():
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "  古代失蜡法铸造仿真系统 - 新增功能测试套件".center(56) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)

    results = []
    results.append(("工艺对比（缺陷率验证）", run_craft_tests()))
    results.append(("透气性分析（气孔率验证）", run_perm_tests()))
    results.append(("虚拟体验（设计自由度验证）", run_virtual_tests()))

    print("\n" + "#" * 60)
    print("#" + "  测试总览".center(56) + "#")
    print("#" * 60)
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name:30s} {status}")

    all_passed = all(r for _, r in results)
    print("#" * 60)
    if all_passed:
        print("\n🎉 所有测试全部通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查失败详情")
        return 1


if __name__ == "__main__":
    sys.exit(main())
