import numpy as np
import matplotlib
matplotlib.use('Agg')          # 批处理下避免 Qt 后端干扰 PDF 保存
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.lines import Line2D

plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 13

# ===================== 数据（严格按 Excel Sheet3 取）=====================
k_list = np.array([0.05, 0.10, 0.20, 0.30])

# NYUD depth RMSE（越低越好）—— 来自 0.05k / k=0.1 / k=0.2 / k=0.3 行
depth_rmse = np.array([
    0.595834963,   # k=5%
    0.5884469906666666,          # k=10%
    0.5970886750000001,   # k=20%
    0.5923485946666667,   # k=30%
])

# NYUD normals mErr（越低越好）
normals_mErr = np.array([
    20.476229473333333,   # k=5%
    20.428107299999997,   # k=10%
    20.467289473333334,   # k=20%
    20.480094923333333,   # k=30%
])

# # 上传字节数（100 轮总字节）
# upload_bytes = np.array([
#     414030082,   # k=5%
#     368013873,   # k=10%
#     550263147,   # k=20%
#     542939993,   # k=30%
# ])

# # 下载字节数（100 轮总字节）
# download_bytes = np.array([
#     595003501,   # k=5%
#     516922605,   # k=10%
#     720832001,   # k=20%
#     874317466,   # k=30%
# ])

# 上传字节数（100 轮总字节）
upload_bytes = np.array([
    368013873,   # k=5%
    414030082,   # k=10%
    550263147,   # k=20%
    542939993,   # k=30%
])

# 下载字节数（100 轮总字节）
download_bytes = np.array([
    516922605,   # k=5%
    595003501,   # k=10%
    720832001,   # k=20%
    874317466,   # k=30%
])

# 每轮总通信量 MiB（上传 + 下载），100 轮
comm_MB = (upload_bytes + download_bytes) / 100 / (1024 ** 2)

# FedAvg 参考值
fedavg_depth   = 0.7858
fedavg_normals = 21.62

# ===================== 相对 FedAvg 误差变化率 =====================
def rel_error(metric, ref):
    return (metric - ref) / ref * 100.0   # 负值 = 比 FedAvg 更好

rel_depth   = rel_error(depth_rmse,  fedavg_depth)
rel_normals = rel_error(normals_mErr, fedavg_normals)

# ===================== 双轴图 =====================
def make_dual_plot(rel, comm, title, fname, ylabel, pareto_idx=1):
    x = np.arange(len(k_list))

    # fig, ax1 = plt.subplots(figsize=(8.2, 5.6), dpi=300)
    fig, ax1 = plt.subplots(figsize=(4.8, 5.6), dpi=300)
    # fig, ax1 = plt.subplots(figsize=(4.2, 5.6), dpi=300)



    ax2 = ax1.twinx()

    # 右轴：柱形（上传 + 下载）
    ax2.bar(
        x, comm, width=0.5,
        color='#cfcfcf', edgecolor='#8c8c8c',
        alpha=0.9, zorder=1
    )
    
    ax2.set_ylabel('Total Com per round (MiB)',
                   color='#555555', fontsize=22)
    ax2.tick_params(axis='y', colors='#555555', labelsize=15)
    ax2.set_ylim(0, comm.max() * 1.35)

    # 左轴：相对误差折线
    ax1.plot(
        x, rel, marker='o', markersize=8,
        linewidth=2.6, color='#1f77b4', zorder=3
    )
    ax1.set_ylabel(ylabel, color='#1f77b4', fontsize=22)
    ax1.tick_params(axis='y', colors='#1f77b4', labelsize=15)
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.2f%%'))

    # 自动放大左轴，凸显小数差异
    ymin, ymax = rel.min(), rel.max()
    pad = max((ymax - ymin) * 0.55, 0.05)
    ax1.set_ylim(ymin - pad, ymax + pad)

    # 只标 Pareto point（k=10%）
    px, py = x[pareto_idx], rel[pareto_idx]
    ax1.scatter([px], [py], color='red', s=110, zorder=5)
    # ax1.annotate(
    #     'Pareto point',
    #     xy=(px, py),
    #     xytext=(px + 0.55, py + (ymax - ymin) * 0.35),
    #     arrowprops=dict(arrowstyle='->', color='red', lw=2),
    #     fontsize=15, color='red', fontweight='bold'
    # )

    ax1.set_xticks(x)
    ax1.set_xticklabels([f'{k}' for k in k_list], fontsize=15)
    ax1.set_xlabel('Rank ratio k', fontsize=22)
    # ax1.set_title(title, fontsize=16, pad=12)
    ax1.grid(True, linestyle='--', alpha=0.3)

    # 让柱形在折线下方
    ax2.set_zorder(ax1.get_zorder() - 1)
    ax1.patch.set_visible(False)

    # 图例
    legend_elements = [
        Line2D([0], [0], color='#1f77b4', marker='o',
               lw=2.6, label='Relative error vs. FedAvg'),
        plt.Rectangle((0, 0), 1, 1, facecolor='#cfcfcf',
                      edgecolor='#8c8c8c', alpha=0.9,
                      label='Total Com per round')
    ]
    # ax1.legend(handles=legend_elements, loc='best', fontsize=20)
    ax1.legend(handles=legend_elements, loc='upper center',
           bbox_to_anchor=(0.5, 1.15), ncol=2, frameon=True, fontsize=12)


    fig.tight_layout()
    fig.savefig(fname, bbox_inches='tight')
    fig.savefig(fname.replace('.png', '.pdf'), bbox_inches='tight')
    plt.close(fig)   # 不再 plt.show()

# ===================== 生成两个图 =====================
# make_dual_plot(
#     rel_depth, comm_MB,
#     '(a) NYUD Depth RMSE: Relative Error vs. Communication',
#     'rank_k_depth.png',
#     'Relative error vs. FedAvg (%)'
# )

# make_dual_plot(
#     rel_normals, comm_MB,
#     '(b) NYUD Normals: Relative Error vs. Communication',
#     'rank_k_normals.png',
#     'Relative error vs. FedAvg (%)'
# )

make_dual_plot(
    rel_normals, comm_MB,
    '(b) NYUD Normals: Relative Error vs. Communication',
    'rank_k_normals.png',
    'Relative error vs. FedAvg (%)'
)