# Trust Boundaries

不受信输入包括 snapshot JSON、provider、contract template 以及 Rust 输出。
这些数据在交给 downstream 系统前必须经过 validation。

受信的本地组件包括 canonical Python、schema 和 validation scripts；这不表示
存在安全审计或 production 保证。

private key、wallet、signing、broadcast、live trading、deployment、gas analysis
与 formal verification 均不在 boundary 内。
