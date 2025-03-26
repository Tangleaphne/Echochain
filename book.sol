// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Echo {
    struct Guider {
        string guidertype;
        address guideraddress;
        string guider_name;
        string description;
        uint256 price_per_hour;
        string imglink;
    }
        
    mapping(uint256 => Guider) public guiders;
    mapping(address =>uint256) public guiderIds;
    uint256 public guiderCount;

    struct Order {
        address provider;
        address receiver;
        string guidertype;
        uint256 amount;
        uint256 startTime;   
        uint256 endTime;     
        bool confirmed;       
        bool completed;
        bool cancelled;
    }

    uint256 public orderIdCounter;
    mapping(uint256 => Order) public orders;
    mapping(address => uint256[]) public providerOrders;  
    mapping(address => uint256[]) public receiverOrders; 

    event OrderCreated(uint256 indexed orderId, address indexed provider, address indexed receiver, uint256 amount);
    event OrderConfirmed(uint256 indexed orderId, address indexed provider);
    event OrderCancelled(uint256 indexed orderId, address cancelledBy);
    event OrderCompleted(uint256 indexed orderId, address indexed receiver);
    event PaymentReleased(uint256 indexed orderId, address indexed to, uint256 amount);
    event GuiderPublished(uint256 indexed guiderId, address indexed guideraddress, uint256 price_per_hour);

    constructor() {
        orderIdCounter = 1; // 初始化订单ID
        guiderCount = 0; // 初始化Guider ID
    }

    function publishGuider( string memory _type, 
                            string memory _name, 
                            string memory _description, 
                            uint256 _price_per_hour, 
                            string memory _imglink
                            ) public {
                                require(_price_per_hour > 0, "Price must be greater than zero");
                                guiderCount++;
                                guiders[guiderCount] = Guider(
                                    _type, 
                                    msg.sender, 
                                    _name, 
                                    _description, 
                                    _price_per_hour, 
                                    _imglink);

                            guiderIds[msg.sender] = guiderCount;
                            emit GuiderPublished(guiderCount, msg.sender, _price_per_hour);
                        }

    function getPricePerHourByAddress(address _guiderAddress) public view returns (uint256) {
        uint256 guiderId = guiderIds[_guiderAddress]; 
        require(guiderId > 0, "Guider not found for this address");
        return guiders[guiderId].price_per_hour; 
    }

    function createOrder(
        address _receiver,   // 接收者地址来自用户输入
        uint256 _guiderId,   // 导游的ID（在前端选择后传入）
        uint256 _startTime,  // 前端传递的开始时间
        uint256 _endTime     // 前端传递的结束时间
    ) external payable {
        require(_endTime > _startTime, "End time must be after start time");
        require(_startTime > block.timestamp, "Start time must be in the future");
        
        Guider memory guider = guiders[_guiderId];
        require(guider.guideraddress != address(0), "Invalid guider");

        uint256 pricePerHour = guider.price_per_hour;
        require(pricePerHour > 0, "Invalid provider price per hour");

        // 计算服务时长（以小时为单位）
        uint256 serviceDuration = (_endTime - _startTime) / 1 hours;
        require(serviceDuration > 0, "Service duration must be at least 1 hour");

        // 计算订单的总金额
        uint256 totalCost = serviceDuration * pricePerHour;
        require(msg.value == totalCost, "Incorrect payment amount");

        uint256 newOrderId = orderIdCounter;
        orders[newOrderId] = Order({
            provider: guider.guideraddress,  // 从 Guider 信息中获取地址
            receiver: _receiver,             // 从用户输入中获取接收者地址
            guidertype: guider.guidertype,   // 从 Guider 获取服务类型
            amount: msg.value,
            startTime: _startTime,
            endTime: _endTime,
            confirmed: false,
            completed: false,
            cancelled: false
        });

        providerOrders[guider.guideraddress].push(newOrderId);
        receiverOrders[_receiver].push(newOrderId);

        orderIdCounter++;

        emit OrderCreated(newOrderId, guider.guideraddress, _receiver, msg.value);
    }
    function confirmOrder(uint256 _orderId) external {
        Order storage order = orders[_orderId];
        require(msg.sender == order.provider, "Only the assigned provider can confirm the order");
        require(!order.confirmed, "Order already confirmed");
        require(order.amount > 0, "Invalid order");

        order.confirmed = true;
        emit OrderConfirmed(_orderId, msg.sender);
    }

    // 服务接收者确认订单完成
    function completeOrder(uint256 _orderId) external {
        Order storage order = orders[_orderId];
        require(msg.sender == order.receiver, "Only the receiver can confirm order completion");
        require(order.confirmed, "Order has not been confirmed by the provider");
        require(!order.completed, "Order already completed");
        require(!order.cancelled, "Cannot complete a cancelled order");

        order.completed = true;
        releasePayment(_orderId);
    }

    // 服务提供者拒绝订单，资金归还给receiver
    function rejectOrder(uint256 _orderId) external {
        Order storage order = orders[_orderId];
        require(msg.sender == order.provider, "Only the assigned provider can reject the order");
        require(!order.confirmed, "Cannot reject a confirmed order");
        require(!order.cancelled, "Order already cancelled");

        order.cancelled = true;

        // 将资金返还给receiver
        address payable receiver = payable(order.receiver);
        uint256 amount = order.amount;
        order.amount = 0;  // 防止重入攻击

        receiver.transfer(amount);
        emit OrderCancelled(_orderId, msg.sender);
    }

    // 内部函数：支付订单
    function releasePayment(uint256 _orderId) internal {
        Order storage order = orders[_orderId];
        require(order.completed, "Order not completed yet");

        address payable provider = payable(order.provider);
        uint256 amount = order.amount;

        // 防止重入攻击，先将余额清零
        order.amount = 0;

        // 将资金转给服务提供者
        provider.transfer(amount);

        emit PaymentReleased(_orderId, order.provider, amount);
    }

    // 自动释放资金（服务结束后24小时自动完成）
    function autoCompleteOrder(uint256 _orderId) external {
        Order storage order = orders[_orderId];
        require(block.timestamp >= order.endTime + 24 hours, "24 hours after service end time required");
        require(!order.completed, "Order already completed");
        require(order.confirmed, "Order has not been confirmed by the provider");
        require(!order.cancelled, "Cannot auto-complete a cancelled order");

        // 标记为已完成，并释放资金
        order.completed = true;
        releasePayment(_orderId);
    }

    // 获取订单状态
    function getOrderStatus(uint256 _orderId) external view returns (bool confirmed, bool completed, bool cancelled, uint256 endTime) {
        Order storage order = orders[_orderId];
        return (order.confirmed, order.completed, order.cancelled, order.endTime);
    }
}
